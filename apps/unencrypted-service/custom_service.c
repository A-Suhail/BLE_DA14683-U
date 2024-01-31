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

/*
 * INC_SVC      :       total included services within service
 * TOT_CHR      :       total characteristics provided by service
 * TOT_DESC     :       total descriptors of characteristics provided
 *
 * CHANGE THIS ACCORDINGLY
 */
#define INC_SVC         0
#define TOT_CHR         3
#define TOT_DESC        1


/*
 * custom services structure
 */
typedef struct {
        ble_service_t svc;                      //default ble service struct
        cs_callbacks_t *cb;                     //custom service callback struct

        //handles
        uint16_t read_char_handle;              //read char handle
        uint16_t write_char_handle;             //write char handle
        uint16_t notify_char_handle;            //notify service handle
        uint16_t notify_cccd_handle;            //notify ccc char handle
} cs_service_t;


static att_error_t read_client_msg(const uint8_t *value)
{
        printf(NEWLINE "Message from client :  %s" NEWLINE, (const char *)value);
        fflush(stdout);
        return ATT_ERROR_OK;
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

        if (cs->cb && cs->cb->notif_changed) {
                cs->cb->notif_changed(conn_idx, ccc_val & GATT_CCC_NOTIFICATIONS);
        }

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

                uint16_t max_len=20;
                uint16_t *temp_len = &max_len;
                void * temp_val = NULL;
                ble_gatts_get_value(cs->read_char_handle, temp_len,temp_val);

                char * store=malloc(strlen(temp_val)+1);
                strncpy(store, temp_val,strlen(temp_val)+1);

                printf(NEWLINE "Message sent to client : %s"NEWLINE, store);
                fflush(stdout);

                ble_gatts_read_cfm(evt->conn_idx, cs->read_char_handle, ATT_ERROR_OK, strlen(store), store);

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
                status = read_client_msg(evt->value);
                goto done;
        }
        if (evt->handle == cs->notify_cccd_handle)
        {

                if(get_u16(evt->value)==1){
                        printf(NEWLINE NEWLINE "Notifications ON");
                        fflush(stdout);
                }
                else{
                        printf(NEWLINE NEWLINE "Notifications OFF");
                        fflush(stdout);
                }

                status = do_notif_ccc_write(cs, evt->conn_idx, evt->offset, evt->length, evt->value);

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
        ble_storage_remove_all(cs->notify_char_handle);
        ble_storage_remove_all(cs->notify_cccd_handle);

        OS_FREE(svc);
}


/*
 * Initializing our custom service here
 */
ble_service_t *chat_service_init(const cs_parameter_t *cs_param, cs_callbacks_t *cb)
{
        cs_service_t *cs;
        uint16_t num_attr;
        att_uuid_t uuid;

        static char* user_msg;
        strcpy(user_msg, cs_param->custom_msg);

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
         * 1 descriptor
         */
        num_attr = ble_gatts_get_num_attr(INC_SVC,TOT_CHR,TOT_DESC);

        //Adding the main service
        ble_uuid_from_string(UUID_CS, &uuid);
        ble_gatts_add_service(&uuid, GATT_SERVICE_PRIMARY, num_attr);


        /*Adding Read Characteristic*/
        ble_uuid_from_string(UUID_CS_READ, &uuid);
        ble_gatts_add_characteristic(&uuid, GATT_PROP_READ, ATT_PERM_READ, strlen(cs_param->custom_msg), flag, NULL, &cs->read_char_handle);

        /*Adding Write Characteristic*/
        ble_uuid_from_string(UUID_CS_WRITE, &uuid);
        ble_gatts_add_characteristic(&uuid, GATT_PROP_WRITE, ATT_PERM_WRITE, 24, 0, NULL, &cs->write_char_handle);

        /*Adding Notify Characteristic*/
        ble_uuid_from_string(UUID_CS_NOTIFY, &uuid);
        ble_gatts_add_characteristic(&uuid, GATT_PROP_NOTIFY, ATT_PERM_NONE, 24, 0, NULL, &cs->notify_char_handle);

        ble_uuid_create16(UUID_GATT_CLIENT_CHAR_CONFIGURATION, &uuid);
        ble_gatts_add_descriptor(&uuid, ATT_PERM_RW, 1, 0, &cs->notify_cccd_handle);


        //this should write custom user message to read service
        ble_gatts_set_value(cs->read_char_handle, strlen(cs_param->custom_msg), cs_param->custom_msg);

        /*register ble service*/
        ble_gatts_register_service(&cs->svc.start_h,&cs->write_char_handle, &cs->notify_char_handle, &cs->notify_cccd_handle, &cs->read_char_handle, 0);


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
//       uint8_t payload[20]; // default ATT_MTU-3
//       uint8_t payload_len;

       ble_storage_get_u16(conn_idx, cs->notify_cccd_handle, &ccc_val);

       if (!(ccc_val & GATT_CCC_NOTIFICATIONS)) {
               return;
       }

       ble_gatts_send_event(conn_idx, cs->notify_char_handle, GATT_EVENT_NOTIFICATION, sizeof(value), value);
}
