/*
 * Custom chat service
 */

#ifndef CS_H_
#define CS_H_

#include "ble_service.h"

typedef void (* mcs_get_char_value_cb_t) (ble_service_t *svc, uint16_t conn_idx);
typedef uint16_t (*block_state_t) (uint16_t  conn_idx);


/*
 * CS application callbacks
 */
typedef struct{
        mcs_get_char_value_cb_t get_characteristic_value;
        block_state_t blocker;
}cs_callbacks_t;

/*
 *function register CS instance
 */
ble_service_t *chat_service_init(cs_callbacks_t *cb);


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
