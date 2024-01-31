#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <string.h>
#include "osal.h"
#include "ble_att.h"
#include "ble_bufops.h"
#include "ble_storage.h"
#include "ble_common.h"
#include "ble_gatts.h"
#include "ble_uuid.h"
#include "custom_service.h"


#define UUID_CS                "0783b03e-8535-b5a0-7140-a304d2492001"
#define UUID_CS_READ_PAIR      "0783b03e-8535-b5a0-7140-a304d2492002"

static const char *cs_read_pair_desc = "Read Data";

typedef struct {
        ble_service_t svc;
        cs_callbacks_t *cb;

        //read service
        uint16_t read_char_handle;              //read char handle

        uint16_t read_char_pair_handle;         //read-pair char handle
} cs_service_t;


void cs_get_char_value_cfm(ble_service_t *svc, uint16_t conn_idx, att_error_t status,
                                                                    const char *value)
{
        cs_service_t *cs = (cs_service_t *) svc;

        /* This function should be used as a response for every read request */
        ble_gatts_read_cfm(conn_idx, cs->read_char_pair_handle, ATT_ERROR_OK, strlen(value), value);
}

static void do_char_value_read(cs_service_t *cs, const ble_evt_gatts_read_req_t *evt)
{

        ble_evt_gap_pair_req_t *pt = (ble_evt_gap_pair_req_t *) cs;
        ble_error_t err = ble_gap_pair(pt->conn_idx,pt->bond);

        if(err==BLE_ERROR_FAILED){
                printf(NEWLINE "BLE_PAIR_REQUEST_FAILED"NEWLINE);
                fflush(stdout);
                return;
        }
        else{
                printf(NEWLINE "BLE_PAIR_REQUEST_SENT"NEWLINE);
                fflush(stdout);
        }

        if(cs->cb->blocker(evt->conn_idx)==0)
        {
                return;
        }

        printf(NEWLINE NEWLINE"DEVICE PAIRED, SENDING DATA NOW");
        fflush(stdout);

        /*
         * Check whether the application has defined a callback function
         * for handling the event.
         */
        if (!cs->cb || !cs->cb->get_characteristic_value) {
                ble_gatts_read_cfm(evt->conn_idx, evt->handle,
                                                   ATT_ERROR_READ_NOT_PERMITTED, 0, NULL);
                return;
        }

        /*
         * The application should provide the requested data to the peer device.
         */
        cs->cb->get_characteristic_value(&cs->svc, evt->conn_idx);

        // callback executed properly

}

static void handle_read_req(ble_service_t *svc, const ble_evt_gatts_read_req_t *evt)
{
        /*
         *handle read request from client
         */

        cs_service_t *cs = (cs_service_t *) svc;

        if(evt->handle == cs->read_char_pair_handle){
                printf(NEWLINE NEWLINE"Encrypted msg characteristic invoked");
                fflush(stdout);
                do_char_value_read(cs, evt);

        }
        else {
                ble_gatts_read_cfm(evt->conn_idx, evt->handle, ATT_ERROR_READ_NOT_PERMITTED, 0, NULL);
        }
}


static void handle_write_req(ble_service_t *svc, const ble_evt_gatts_write_req_t *evt)
{
        ble_gatts_write_cfm(evt->conn_idx, evt->handle, ATT_ERROR_OK);
}


static void cleanup(ble_service_t *svc)
{
        cs_service_t *cs = (cs_service_t *) svc;
        ble_storage_remove_all(cs->read_char_pair_handle);

        OS_FREE(svc);
}

ble_service_t *chat_service_init(cs_callbacks_t *cb)
{
        cs_service_t *cs;
        uint16_t num_attr;
        att_uuid_t uuid;
        uint16_t cs_read_pair_desc_h;

        //allocate memory for service handle
        cs = OS_MALLOC(sizeof(*cs));
        memset(cs, 0, sizeof(*cs));

        num_attr = ble_gatts_get_num_attr(0,1,1);

        gatts_flag_t __attribute__((unused)) flag = GATTS_FLAG_CHAR_READ_REQ;

        ble_uuid_from_string(UUID_CS, &uuid);
        ble_gatts_add_service(&uuid, GATT_SERVICE_PRIMARY, num_attr);

        /*pairing request read characteristic*/
        ble_uuid_from_string(UUID_CS_READ_PAIR, &uuid);
        ble_gatts_add_characteristic(&uuid, GATT_PROP_READ, ATT_PERM_READ, 20, flag, NULL, &cs->read_char_pair_handle);
        ble_uuid_create16(UUID_GATT_CHAR_USER_DESCRIPTION, &uuid);
        ble_gatts_add_descriptor(&uuid, ATT_PERM_READ, strlen(cs_read_pair_desc), 0, &cs_read_pair_desc_h);


        /*register ble service*/
        ble_gatts_register_service(&cs->svc.start_h,&cs->read_char_pair_handle,&cs_read_pair_desc_h, 0);

        ble_gatts_set_value(cs_read_pair_desc_h, strlen(cs_read_pair_desc), cs_read_pair_desc);

        //declare handlers for specific ble events
        cs->svc.write_req = handle_write_req;
        cs->svc.read_req = handle_read_req;
        cs->svc.end_h = cs->svc.start_h + num_attr;
        cs->svc.cleanup = cleanup;
        cs->cb = cb;

        ble_service_add(&cs->svc);

        return &cs->svc;

}
