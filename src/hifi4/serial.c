// Example code for interacting with serial_irq.c
//
// Copyright (C) 2018  Kevin O'Connor <kevin@koconnor.net>
//
// This file may be distributed under the terms of the GNU GPLv3 license.

#include <FreeRTOS.h>
#include <hal_uart.h>
#include "autoconf.h" // Include configuration header
#include "board/serial_irq.h" // serial_get_tx_byte
#include "sched.h" // DECL_INIT

// Dynamically select UART and IRQ based on configuration


    #if CONFIG_HIFI4_SERIAL_UART0
        #define UARTx UART_0
        #define UARTx_IRQn UART0_IRQ_IRQn
    #elif CONFIG_HIFI4_SERIAL_UART1
        #define UARTx UART_1
        #define UARTx_IRQn UART1_IRQ_IRQn
    #elif CONFIG_HIFI4_SERIAL_UART2
        #define UARTx UART_2
        #define UARTx_IRQn UART2_IRQ_IRQn
    #elif CONFIG_HIFI4_SERIAL_UART3
        #define UARTx UART_0
        #define UARTx_IRQn UART3_IRQ_IRQn
    #endif

void
UARTx_IRQHandler(int32_t dev_id, uint8_t val)
{
    if (dev_id == UARTx)
        serial_rx_byte(val);
}

void
serial_init(void)
{
    _uart_config_t uart_config;

    switch (CONFIG_SERIAL_BAUD) {
    case 300:
        uart_config.baudrate = UART_BAUDRATE_300;
        break;
    case 600:
        uart_config.baudrate = UART_BAUDRATE_600;
        break;
    case 1200:
        uart_config.baudrate = UART_BAUDRATE_1200;
        break;
    case 2400:
        uart_config.baudrate = UART_BAUDRATE_2400;
        break;
    case 4800:
        uart_config.baudrate = UART_BAUDRATE_4800;
        break;
    case 9600:
        uart_config.baudrate = UART_BAUDRATE_9600;
        break;
    case 19200:
        uart_config.baudrate = UART_BAUDRATE_19200;
        break;
    case 38400:
        uart_config.baudrate = UART_BAUDRATE_38400;
        break;
    case 57600:
        uart_config.baudrate = UART_BAUDRATE_57600;
        break;
    case 115200:
        uart_config.baudrate = UART_BAUDRATE_115200;
        break;
    case 230400:
        uart_config.baudrate = UART_BAUDRATE_230400;
        break;
    case 576000:
        uart_config.baudrate = UART_BAUDRATE_576000;
        break;
    case 921600:
        uart_config.baudrate = UART_BAUDRATE_921600;
        break;
    case 1000000:
        uart_config.baudrate = UART_BAUDRATE_1000000;
        break;
    case 1500000:
        uart_config.baudrate = UART_BAUDRATE_1500000;
        break;
    case 3000000:
        uart_config.baudrate = UART_BAUDRATE_3000000;
        break;
    case 4000000:
        uart_config.baudrate = UART_BAUDRATE_4000000;
        break;
    default:
        // Using default baudrate 115200
        uart_config.baudrate = UART_BAUDRATE_115200;
        break;
    }

    uart_config.word_length = UART_WORD_LENGTH_8;
    uart_config.stop_bit = UART_STOP_BIT_1;
    uart_config.parity = UART_PARITY_NONE;

    hal_uart_init(UARTx);
    hal_uart_control(UARTx, 0, &uart_config);
    hal_uart_disable_flowcontrol(UARTx);
    hal_uart_register_irq(UARTx_IRQHandler);
}
DECL_INIT(serial_init);

// Todo: Should rewrite to use TX FIFO and TX irq
void
serial_enable_tx_irq(void)
{
    for (;;) {
        uint8_t data;
        int ret = serial_get_tx_byte(&data);
        if (ret) {
            // No more data to send
            break;
        }
        hal_uart_put_char(UARTx, data);
    }
}
