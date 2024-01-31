/*
 * Custom chat service
 */

#ifndef CS_H_
#define CS_H_

#include "ble_service.h"


typedef void (*cs_msg_read_cb_t) (ble_service_t *svc, uint16_t conn_idx);

typedef void (*cs_msg_write_cb_t) (ble_service_t *svc, uint16_t conn_idx, uint16_t *length, char *value);

typedef void (* mcs_get_char_value_cb_t) (ble_service_t *svc, uint16_t conn_idx);


/*
 * CS application callbacks
 */
typedef struct{
        cs_msg_read_cb_t received_data;
        cs_msg_write_cb_t send_data;
}cs_callbacks_t;

/*
 * defining all the parameters our service take to initialize
 */
typedef struct{
        const char * custom_msg;
}cs_parameter_t;

/*
 * save the last state in here of user write
 */
typedef struct{
        char * write;
}cs_last_state_t;

/*
 *function register CS instance
 */
ble_service_t *custom_service_init(cs_callbacks_t *cb);


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
