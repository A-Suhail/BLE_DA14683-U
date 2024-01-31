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


/*
 * UUIDS FOR SERVICE AND ITS CHRACTERISTICS
 */
#define UUID_CS                "0783b03e-8535-b5a0-7140-a304d2492001"
#define UUID_CS_WRITE          "0783b03e-8535-b5a0-7140-a304d2492002"
#define UUID_CS_READ           "0783b03e-8535-b5a0-7140-a304d2492003"
#define UUID_CS_NOTIFY         "0783b03e-8535-b5a0-7140-a304d2492004"

static const char *cs_read_desc = "Read Data";
static const char *cs_write_desc = "Write Data";
static const char *cs_notify_desc = "Notify Data";

/*
 * INC_SVC      :       total included services within service
 * TOT_CHR      :       total characteristics provided by service
 * TOT_DESC     :       total descriptors of characteristics provided
 *
 * CHANGE THIS ACCORDINGLY
 */
#define INC_SVC         0
#define TOT_CHR         3
#define TOT_DESC        4

#define MAX_MSG_LEN     30


/*
 * custom services structure
 */
typedef struct {
        ble_service_t svc;                      //default ble service struct
        cs_callbacks_t *cb;                     //custom service callback struct

        //handles
        uint16_t read_char_handle;              //read char handle
        uint16_t write_char_handle;             //write char handle
        uint16_t notify_char_val_handle;        //notify service handle
        uint16_t notify_cccd_handle;            //notify ccc char handle

} cs_service_t;

static cs_last_state_t cs_last_state = {
        .write = NULL,
};

static bool send_data(cs_service_t *cs, uint16_t conn_idx, uint16_t length, const uint8_t *value)
{
        uint8_t status;

        status = ble_gatts_send_event(conn_idx, cs->notify_char_val_handle, GATT_EVENT_NOTIFICATION, length, (const char*)value);

        return status == BLE_STATUS_OK ? true : false;
}

static void read_client_msg(cs_service_t *cs,  uint16_t conn_idx,
                                                uint16_t offset, uint16_t length, const uint8_t *value)
{
         /*
         * implement the writing to notification service now
         */

        uint16_t ccc = 0x0000;

        //check if notifications are enabled
        ble_storage_get_u16(conn_idx, cs->notify_cccd_handle, &ccc);


        if (cs_last_state.write != NULL) {
            free(cs_last_state.write); // Free any previously allocated memory
        }

        cs_last_state.write = malloc(strlen((const char*)value) + 1); // Allocate memory for the new value
        strcpy(cs_last_state.write, (const char*)value); // Copy the data into the allocated memory


        if (!(ccc & GATT_CCC_NOTIFICATIONS)) {
                printf(NEWLINE "WARN: NOTIFICATIONS ARE OFF !" NEWLINE);
                fflush(stdout);
                return;
        }

        printf(NEWLINE "MESSAGE FROM CLIENT :  %s" NEWLINE, (const uint8_t *)value);
        fflush(stdout);

        send_data(cs, conn_idx, length, value);
}

static att_error_t do_notif_ccc_write(cs_service_t *cs, uint16_t conn_idx, uint16_t offset, uint16_t length, const uint8_t *value)
{
        uint16_t ccc_val;

        if (offset) {
                return ATT_ERROR_ATTRIBUTE_NOT_LONG;
        }

        if (length != sizeof(uint16_t)) {
                return ATT_ERROR_APPLICATION_ERROR;
        }

        ccc_val = get_u16(value);

        ble_storage_put_u32(conn_idx, cs->notify_cccd_handle, ccc_val, true);


        return ATT_ERROR_OK;
}


static void handle_read_req(ble_service_t *svc, const ble_evt_gatts_read_req_t *evt)
{

        cs_service_t *cs = (cs_service_t *) svc;

        if (evt->handle == cs->notify_cccd_handle) {
                uint16_t ccc_val = 0;

                ble_storage_get_u16(evt->conn_idx, cs->notify_cccd_handle, &ccc_val);

                // we're little-endian, ok to use value as-is
                ble_gatts_read_cfm(evt->conn_idx, evt->handle, ATT_ERROR_OK, sizeof(uint16_t), &ccc_val);
        }

        else if(evt->handle == cs->read_char_handle){

                if (cs_last_state.write != NULL) {
                        printf(NEWLINE "MESSAGE SENT TO CLIENT : %s"NEWLINE, (char*)cs_last_state.write);
                        fflush(stdout);
                        ble_gatts_read_cfm(evt->conn_idx, cs->read_char_handle, ATT_ERROR_OK, strlen(cs_last_state.write), (const char*)cs_last_state.write);
                        return;
                }

                uint16_t msg_len;
                char * msg_val = malloc(MAX_MSG_LEN);

                cs->cb->send_data(svc,evt->conn_idx,&msg_len,msg_val);

                ble_error_t error = ble_gatts_read_cfm(evt->conn_idx, cs->read_char_handle, ATT_ERROR_OK, msg_len, msg_val);

                if (error == 0){
                        printf(NEWLINE "MESSAGE SENT TO CLIENT : %s"NEWLINE, msg_val);
                        fflush(stdout);
                }

                free(msg_val);

        }

        else {
                ble_gatts_read_cfm(evt->conn_idx, evt->handle, ATT_ERROR_READ_NOT_PERMITTED, 0, NULL);
        }
}


static void handle_write_req(ble_service_t *svc, const ble_evt_gatts_write_req_t *evt)
{
        /*
         * handle write request from client
         */

        cs_service_t *cs = (cs_service_t *) svc;
        att_error_t status = ATT_ERROR_ATTRIBUTE_NOT_FOUND;


        if (evt->handle == cs->write_char_handle)
        {
                read_client_msg(cs, evt->conn_idx, evt->offset, evt->length, evt->value);
                goto done;
        }
        if (evt->handle == cs->notify_cccd_handle)
        {

                if(get_u16(evt->value)==1){
                        printf(NEWLINE "NOTIFICATIONS ON" NEWLINE);
                        fflush(stdout);
                }
                else{
                        printf(NEWLINE "NOTIFICATIONS OFF" NEWLINE);
                        fflush(stdout);
                }

                status = do_notif_ccc_write(cs, evt->conn_idx, evt->offset, evt->length, evt->value);


                if (cs_last_state.write != NULL) {
                        send_data(cs, evt->conn_idx, strlen(cs_last_state.write), (const uint8_t *)cs_last_state.write);
                }

                goto done;
        }


done:
        ble_gatts_write_cfm(evt->conn_idx, evt->handle, status);
}


static void cleanup(ble_service_t *svc)
{
        cs_service_t *cs = (cs_service_t *) svc;

        ble_storage_remove_all(cs->write_char_handle);
        ble_storage_remove_all(cs->read_char_handle);
        ble_storage_remove_all(cs->notify_char_val_handle);
        ble_storage_remove_all(cs->notify_cccd_handle);

        OS_FREE(svc);
}


/*
 * Initializing our custom service here
 */

ble_service_t *custom_service_init(cs_callbacks_t *cb)
{
        uint16_t cs_read_desc_h, cs_write_desc_h, cs_notify_desc_h;
        cs_service_t *cs;
        uint16_t num_attr;
        att_uuid_t uuid;

        /*
         * use this flag if want to custom handle read requests
         */
        gatts_flag_t __attribute__((unused)) flag = GATTS_FLAG_CHAR_READ_REQ;

        //allocate memory for service handle
        cs = OS_MALLOC(sizeof(*cs));
        memset(cs, 0, sizeof(*cs));

        /*
         * 0 inc services
         * 3 characteristics
         * 4 descriptor
         */
        num_attr = ble_gatts_get_num_attr(INC_SVC,TOT_CHR,TOT_DESC);

        //Adding the main service
        ble_uuid_from_string(UUID_CS, &uuid);
        ble_gatts_add_service(&uuid, GATT_SERVICE_PRIMARY, num_attr);


        /*Adding Read Characteristic*/
        ble_uuid_from_string(UUID_CS_READ, &uuid);
        ble_gatts_add_characteristic(&uuid, GATT_PROP_READ, ATT_PERM_READ_ENCRYPT, MAX_MSG_LEN, flag, NULL, &cs->read_char_handle);
        ble_uuid_create16(UUID_GATT_CHAR_USER_DESCRIPTION, &uuid);
        ble_gatts_add_descriptor(&uuid, ATT_PERM_READ, strlen(cs_read_desc), 0, &cs_read_desc_h);


        /*Adding Write Characteristic*/
        ble_uuid_from_string(UUID_CS_WRITE, &uuid);
        ble_gatts_add_characteristic(&uuid, GATT_PROP_WRITE, ATT_PERM_WRITE_ENCRYPT, MAX_MSG_LEN, 0, NULL, &cs->write_char_handle);
        ble_uuid_create16(UUID_GATT_CHAR_USER_DESCRIPTION, &uuid);
        ble_gatts_add_descriptor(&uuid, ATT_PERM_READ, strlen(cs_write_desc), 0, &cs_write_desc_h);


        /*Adding Notify Characteristic*/
        ble_uuid_from_string(UUID_CS_NOTIFY, &uuid);
        ble_gatts_add_characteristic(&uuid, GATT_PROP_NOTIFY, ATT_PERM_NONE, MAX_MSG_LEN, 0, NULL, &cs->notify_char_val_handle);

        ble_uuid_create16(UUID_GATT_CLIENT_CHAR_CONFIGURATION, &uuid);
        ble_gatts_add_descriptor(&uuid, ATT_PERM_READ|ATT_PERM_WRITE_ENCRYPT, 1, 0, &cs->notify_cccd_handle);
        ble_uuid_create16(UUID_GATT_CHAR_USER_DESCRIPTION, &uuid);
        ble_gatts_add_descriptor(&uuid, ATT_PERM_READ, strlen(cs_notify_desc), 0, &cs_notify_desc_h);

        /*register ble service*/
        ble_gatts_register_service(&cs->svc.start_h,&cs->write_char_handle, &cs->notify_char_val_handle, &cs->notify_cccd_handle,
                                                &cs->read_char_handle,&cs_read_desc_h, &cs_write_desc_h, &cs_notify_desc_h, 0);


        // set the value of descriptors
        ble_gatts_set_value(cs_read_desc_h, strlen(cs_read_desc), cs_read_desc);
        ble_gatts_set_value(cs_write_desc_h, strlen(cs_write_desc), cs_write_desc);
        ble_gatts_set_value(cs_notify_desc_h, strlen(cs_notify_desc), cs_notify_desc);


        //declare handlers for specific ble events
        cs->svc.write_req = handle_write_req;
        cs->svc.read_req = handle_read_req;
        cs->svc.end_h = cs->svc.start_h + num_attr;
        cs->svc.cleanup = cleanup;
        cs->cb = cb;

        ble_service_add(&cs->svc);

        return &cs->svc;

}

void cs_notify(ble_service_t *svc, uint16_t conn_idx, const int * value)
{
       cs_service_t *cs = (cs_service_t *) svc;
       uint16_t ccc_val = 0;

       ble_storage_get_u16(conn_idx, cs->notify_cccd_handle, &ccc_val);

       if (!(ccc_val & GATT_CCC_NOTIFICATIONS)) {
               return;
       }

       ble_gatts_send_event(conn_idx, cs->notify_char_val_handle, GATT_EVENT_NOTIFICATION, sizeof(value), value);
}
