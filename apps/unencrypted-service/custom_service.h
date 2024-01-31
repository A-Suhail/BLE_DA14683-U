/*
 * Custom chat service
 */

#ifndef CS_H_
#define CS_H_

#include "ble_service.h"


typedef void (*cs_msg_read_cb_t) (ble_service_t *svc, uint16_t conn_idx);

typedef void (*cs_msg_write_cb_t) (ble_service_t *svc, uint16_t conn_idx, const uint8_t *value);

typedef void (* cs_notification_changed_cb_t) (uint16_t conn_idx, bool enabled);

typedef void (* mcs_get_char_value_cb_t) (ble_service_t *svc, uint16_t conn_idx);


/*
 * CS application callbacks
 */
typedef struct{
        cs_msg_read_cb_t received_data;
        cs_msg_write_cb_t send_data;
        cs_notification_changed_cb_t notif_changed;
}cs_callbacks_t;

/*
 * defining all the parameters our service take to initialize
 */
typedef struct{
        const char * custom_msg;
}cs_parameter_t;

/*
 *function register CS instance
 */
ble_service_t *chat_service_init(const cs_parameter_t *cs_param, cs_callbacks_t *cb);


/**
 * Notify CS value to client *
 */
void cs_notify(ble_service_t *svc, uint16_t conn_idx, const int * value);

/*
 * This function should be called by the application as a response to a read request
 *
 * \param[in] svc       service instance
 * \param[in] conn_idx  connection index
 * \param[in] status    ATT error
 * \param[in] value     attribute value
 */
void cs_get_char_value_cfm(ble_service_t *svc, uint16_t conn_idx, att_error_t status, const char *value);


#endif /* CS_H_ */
