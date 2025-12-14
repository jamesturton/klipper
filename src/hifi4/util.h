#include <stdint.h>
#include <stddef.h>

void *memcpy(void *restrict dest, const void *restrict src, size_t n);
void *memset(void *restrict dest, int c, size_t n);

inline void write_reg(uint32_t addr, uint32_t val){
  *((volatile unsigned long *)(addr)) = val;
}

inline uint32_t read_reg(uint32_t addr){
  return *((volatile unsigned long *)(addr));
}

void set_bit(uint32_t addr, uint8_t bit);

void clear_bit(uint32_t addr, uint8_t bit);

void hw_usleep(uint32_t usec);
void uart_putc(char c);
void print(const char *s);
void print_hex(uint32_t val);

void *malloc(size_t size);

int xt_sprintf(char * str, const char * format, ...);
int xt_printf(const char *format, ...);
