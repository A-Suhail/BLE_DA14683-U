/**
 ****************************************************************************************
 *
 * @file ble_peripheral_task.c
 *
 * @brief BLE peripheral task
 *
 * Copyright (C) 2015-2018 Dialog Semiconductor.
 * This computer program includes Confidential, Proprietary Information
 * of Dialog Semiconductor. All Rights Reserved.
 *
 ****************************************************************************************
 */

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "osal.h"
#include "sys_watchdog.h"
#include "ble_att.h"
#include "ble_common.h"
#include "ble_gap.h"
#include "ble_gatts.h"
#include "ble_service.h"
#include "ble_uuid.h"
#include "co_utils.h"
#include "ble_l2cap.h"
#include "util/list.h"

#include "ble_peripheral_config.h"
#include "bas.h"
#include "cts.h"
#include "dis.h"
#include "scps.h"


#include "custom_service.h"


extern uint8_t *ptr_ble_flag;

/*
 * Notification bits reservation
 * bit #0 is always assigned to BLE event queue notification
 */

#define CS_TIMER_NOTIF  (1 << 1)  // NOTIFICATION FROM NOTIFY CHARACTERISTIC
#define ADV_TIMER_NOTIF (1 << 2)  // NOTIFICATION FROM ADVERTISING TIMER


/* Active connection index used to send measurements */
INITIALISED_PRIVILEGED_DATA static uint16_t active_conn_idx = BLE_CONN_IDX_INVALID;

/*
 * PXP Update connection parameters notif mask
 */
#define PXP_UPDATE_CONN_PARAM_NOTIF     (1 << 3)

/*
 * BLE peripheral advertising data
 */
static const uint8_t adv_data[] = {
        0x12, GAP_DATA_TYPE_LOCAL_NAME,
        'D', 'i', 'a', 'l', 'o', 'g', ' ', 'P', 'e', 'r', 'i', 'p', 'h', 'e', 'r', 'a', 'l'
};

/* Timer used to switch from "fast connection" to "reduced power" advertising intervals */
PRIVILEGED_DATA static OS_TIMER adv_timer;

/*
 *Variable to hold the handle of the task that runs the BLE peripheral application code.
 *The handle is used to monitor the task's execution and to send task notifications to it.
 */
static OS_TASK ble_peripheral_task_handle;


typedef enum {
        ADV_INTERVAL_FAST = 0,
        ADV_INTERVAL_POWER = 1,
} adv_setting_t;

struct device {
        struct device *next;
        bd_address_t addr;
};

typedef struct {
        void           *next;

        bool            expired;

        uint16_t        conn_idx; ///< Connection index

        OS_TIMER        param_timer;
        OS_TASK         current_task;
} conn_dev_t;

/* List of devices waiting for connection parameters update */
PRIVILEGED_DATA static void *param_connections;


/*
 * PXP advertising interval values
 *
 * Recommended advertising interval values as defined by PXP specification. By default "fast connection"
 * is used.
 */
static const struct {
        uint16_t min;
        uint16_t max;
} adv_intervals[2] = {
        // "fast connection" interval values
        {
                .min = BLE_ADV_INTERVAL_FROM_MS(20),      // 20ms
                .max = BLE_ADV_INTERVAL_FROM_MS(30),      // 30ms
        },
        // "reduced power" interval values
        {
                .min = BLE_ADV_INTERVAL_FROM_MS(1000),    // 1000ms
                .max = BLE_ADV_INTERVAL_FROM_MS(1500),    // 1500ms
        }
};

/*
 * Main code
 */

#if !dg_configSUOTA_SUPPORT || PX_REPORTER_SUOTA_POWER_SAVING
/* Update connection parameters */
static void conn_param_update(uint16_t conn_idx)
{
        gap_conn_params_t cp;

        cp.interval_min = defaultBLE_PPCP_INTERVAL_MIN;
        cp.interval_max = defaultBLE_PPCP_INTERVAL_MAX;
        cp.slave_latency = defaultBLE_PPCP_SLAVE_LATENCY;
        cp.sup_timeout = defaultBLE_PPCP_SUP_TIMEOUT;

        ble_gap_conn_param_update(conn_idx, &cp);
}
#endif


static void set_advertising_interval(adv_setting_t setting)
{
        uint16_t min = adv_intervals[setting].min;
        uint16_t max = adv_intervals[setting].max;

        ble_gap_adv_intv_set(min, max);
}

static void handle_evt_gap_connected(ble_evt_gap_connected_t *evt)
{
        if (active_conn_idx == BLE_CONN_IDX_INVALID) {
                active_conn_idx = evt->conn_idx;
                ble_gap_adv_stop();
        }

        bool bond=false;
        ble_gap_is_bonded(evt->conn_idx, &bond);

        if(bond==1){
                printf(NEWLINE "DEVICE IS BONDED" NEWLINE);
                fflush(stdout);
        }

}

static void handle_evt_gap_disconnected(ble_evt_gap_disconnected_t *evt)
{

//        if (active_conn_idx == evt->conn_idx) {
//                active_conn_idx = BLE_CONN_IDX_INVALID;
//
//                OS_TIMER_STOP(adv_timer, OS_TIMER_FOREVER);
//                ble_gap_adv_stop();
//
//                /* Switch back to fast advertising interval. */
//                set_advertising_interval(ADV_INTERVAL_FAST);
//                ble_gap_adv_start(GAP_CONN_MODE_UNDIRECTED);
//                OS_TIMER_START(adv_timer, OS_TIMER_FOREVER);
//                printf(NEWLINE"ADVERTISING STARTED..."NEWLINE);
//                fflush(stdout);
//
//        }

        /* Switch back to fast advertising interval. */
       set_advertising_interval(ADV_INTERVAL_FAST);
       ble_gap_adv_start(GAP_CONN_MODE_UNDIRECTED);
       OS_TIMER_START(adv_timer, OS_TIMER_FOREVER);
       printf(NEWLINE"ADVERTISING STARTED..."NEWLINE);
       fflush(stdout);
}


/*
 * Custom callbacks for chat service
 */
#if CFG_CUSTOM_SERVICE

static void cs_msg_read_cb(ble_service_t *svc, uint16_t conn_idx)
{
        // Will leave this empty for future expansion
}

static void cs_msg_write_cb(ble_service_t *svc, uint16_t conn_idx, uint16_t *length, char *value)
{
        //Send data implementation
        const char* custom_msg = "Greetings Traveler!";

        *length = strlen(custom_msg);
        strcpy(value,custom_msg);
}


static cs_callbacks_t cs_callbacks =
{
        .received_data=cs_msg_read_cb,   // this to be used to work on received data from write char
        .send_data=cs_msg_write_cb,      // this to be used to write data to read char for client
};


#endif

static void adv_timer_cb(TimerHandle_t timer)
{
        OS_TASK task = (OS_TASK) OS_TIMER_GET_TIMER_ID(timer);

        OS_TASK_NOTIFY(task, ADV_TIMER_NOTIF, OS_NOTIFY_SET_BITS);
}

void ble_peripheral_task(void *params)
{
        int8_t wdog_id;

        ble_service_t *svc;

        // in case services which do not use svc are all disabled, just surpress -Wunused-variable
        (void) svc;

        /* register ble_peripheral task to be monitored by watchdog */
        wdog_id = sys_watchdog_register(false);

        ble_peripheral_task_handle = OS_GET_CURRENT_TASK();

        srand(time(NULL));

        ble_peripheral_start();
        ble_register_app();

        ble_gap_device_name_set("Dialog Peripheral", ATT_PERM_READ);


#if CFG_CUSTOM_SERVICE

        custom_service_init(&cs_callbacks);


        /*
         * Create timer for controlling advertising mode. We need to set any non-zero period (i.e. 1)
         * but this will be changed later, when timer is started.
         */
        adv_timer = OS_TIMER_CREATE("adv", /* don't care */ 1, OS_TIMER_FAIL,
                                                (void *) OS_GET_CURRENT_TASK(), adv_timer_cb);
        OS_ASSERT(adv_timer);
#endif

        ble_gap_adv_data_set(sizeof(adv_data), adv_data, 0, NULL);
        ble_gap_adv_start(GAP_CONN_MODE_UNDIRECTED);
        printf(NEWLINE"ADVERTISING STARTED..."NEWLINE);
        fflush(stdout);


        for (;;) {
                OS_BASE_TYPE ret;
                uint32_t notif;

                /* notify watchdog on each loop */
                sys_watchdog_notify(wdog_id);

                /* suspend watchdog while blocking on OS_TASK_NOTIFY_WAIT() */
                sys_watchdog_suspend(wdog_id);

                /*
                 * Wait on any of the notification bits, then clear them all
                 */
                ret = OS_TASK_NOTIFY_WAIT(0, OS_TASK_NOTIFY_ALL_BITS, &notif, OS_TASK_NOTIFY_FOREVER);
                /* Blocks forever waiting for task notification. The return value must be OS_OK */
                OS_ASSERT(ret == OS_OK);

                /* resume watchdog */
                sys_watchdog_notify_and_resume(wdog_id);


                /* notified from BLE manager, can get event */
                if (notif & BLE_APP_NOTIFY_MASK) {
                        ble_evt_hdr_t *hdr;

                        hdr = ble_get_event(false);
                        if (!hdr) {
                                goto no_event;
                        }

                        if (!ble_service_handle_event(hdr)) {
                                switch (hdr->evt_code) {
                                case BLE_EVT_GAP_CONNECTED:
                                        printf(NEWLINE "BLE_CONNECTED" NEWLINE);

                                        handle_evt_gap_connected((ble_evt_gap_connected_t *) hdr);
                                        *ptr_ble_flag = 1;
                                        break;

                                case BLE_EVT_GAP_DISCONNECTED:
                                        printf(NEWLINE "BLE_DISCONNECTED"NEWLINE);
                                        fflush(stdout);
                                        handle_evt_gap_disconnected((ble_evt_gap_disconnected_t *) hdr);
                                        *ptr_ble_flag = 0;
                                        break;

                                case BLE_EVT_GAP_PAIR_REQ:
                                        printf(NEWLINE "BLE_PAIR_REQ_MAIN"NEWLINE);

                                        ble_error_t ret;

                                        ble_evt_gap_pair_req_t *evt = (ble_evt_gap_pair_req_t *) hdr;
                                        ret=ble_gap_pair_reply(evt->conn_idx, true, evt->bond);

                                        if(ret==BLE_ERROR_FAILED){
                                                printf(NEWLINE "BLE_PAIR_REQUEST_FAILED_MAIN"NEWLINE);
                                                fflush(stdout);
                                        }
                                        else{
                                                printf(NEWLINE "BLE_PAIR_REQUEST_SENT_MAIN"NEWLINE);
                                                fflush(stdout);
                                        }

                                        break;

                                case BLE_EVT_GAP_PAIR_COMPLETED:
                                        printf(NEWLINE "BLE_PAIR_PROCESS_COMPLETED"NEWLINE);
                                        fflush(stdout);

                                        break;

                                default:
                                        ble_handle_event_default(hdr);
                                        break;
                                }
                        }

                        OS_FREE(hdr);

no_event:
                        // notify again if there are more events to process in queue
                        if (ble_has_event()) {
                                OS_TASK_NOTIFY(OS_GET_CURRENT_TASK(), BLE_APP_NOTIFY_MASK, eSetBits);
                        }
                }


                /* Fast connection timer expired, try to set reduced power connection parameters */
                if (notif & PXP_UPDATE_CONN_PARAM_NOTIF) {
                        conn_dev_t *conn_dev = param_connections;

                        if (conn_dev && conn_dev->expired) {
                                param_connections = conn_dev->next;

#if dg_configSUOTA_SUPPORT
                                /*
                                 * Ignore this if SUOTA is ongoing - it's possible to start SUOTA
                                 * before reduced power parameters are applied so this would switch
                                 * to a long connection interval.
                                 */
                                if (!suota_ongoing) {
#endif
#if !dg_configSUOTA_SUPPORT || PX_REPORTER_SUOTA_POWER_SAVING
                                        conn_param_update(conn_dev->conn_idx);
#endif
#if dg_configSUOTA_SUPPORT
                                }
#endif

                                OS_TIMER_DELETE(conn_dev->param_timer, OS_TIMER_FOREVER);
                                OS_FREE(conn_dev);

                                /*
                                 * If the queue is not empty reset bit and check if timer expired
                                 * next time
                                 */
                                if (param_connections) {
                                        OS_TASK_NOTIFY(OS_GET_CURRENT_TASK(),
                                                PXP_UPDATE_CONN_PARAM_NOTIF, OS_NOTIFY_SET_BITS);
                                }
                        }
                }

        }
}
