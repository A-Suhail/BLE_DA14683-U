/**
 ****************************************************************************************
 *
 * @file util.c
 *
 * @brief Utility functions
 *
 * Copyright (C) 2015-2017 Dialog Semiconductor.
 * This computer program includes Confidential, Proprietary Information
 * of Dialog Semiconductor. All Rights Reserved.
 *
 ****************************************************************************************
 */

#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "cli_common.h"
#include "uartboot_types.h"
#include "partition_def.h"

#if defined(_MSC_VER) && _MSC_VER < 1800
#define strtoull _strtoui64
#endif

void dump_hex(uint32_t addr, uint8_t *buf, size_t size, unsigned int width)
{
        uint32_t c_addr, e_addr;
        char line[33] = { '\0' };
        uint32_t bnd_mask;

        /* width should be power of 2 */
        if (!width || width > 32 || (width & (width - 1))) {
                return;
        }

        /* mask for checking hexdump row boundary */
        bnd_mask = width - 1;

        /* align "current" and "end" addresses to cover full hexdump rows */
        c_addr = addr & ~bnd_mask;
        e_addr = (addr + size + bnd_mask) & ~bnd_mask;

        for (; c_addr < e_addr; c_addr++) {
                unsigned int idx = c_addr - addr;

                if ((c_addr & bnd_mask) == 0) {
                        printf("%08X   ", c_addr);
                }

                if (idx < 0 || idx >= size) {
                        printf("   ");
                        line[c_addr & bnd_mask] = ' ';
                } else {
                        printf("%02X ", buf[idx]);
                        line[c_addr & bnd_mask] = (buf[idx] >= 32 && buf[idx] <= 127 ? buf[idx] : '.');
                }

                if ((c_addr & bnd_mask) == bnd_mask) {
                        printf("  %s\n", line);
                }
        }
}

void dump_otp(uint32_t cell_offset, uint32_t *buf, size_t len)
{
        unsigned int i, j;

        for (i = 0; i < len; i += 2) {
                char line[9] = { '\0' };

                uint64_t val;

                val = buf[i];
                if (i + 1 < len) {
                        val |= ((uint64_t) buf[i + 1] << 32);
                }

                printf("%04X   ", cell_offset);

                for (j = 0; j < 8; j++) {
                        uint8_t v = val & 0xFF;

                        printf("%02X ", v);
                        line[j] = (v >= 32 && v <= 127 ? v : '.');

                        val >>= 8;
                }

                printf("  %s\n", line);

                cell_offset++;
        }
}

static char *file_skip_field(char *s)
{
        if (!s) {
                return NULL;
        }

        s = strchr(s, '\t');

        return s ? ++s : NULL;
}

static bool file_get_value(char *s, uint64_t *val, int base)
{
        char *end_p;
        uint64_t ret;

        if (!s) {
                return false;
        }

        ret = strtoull(s, &end_p, base);
        if (s == end_p) {
                return false;
        }

        *val = ret;

        return true;
}

bool parse_otp_file(const char *fname, otp_file_cb value_cb)
{
        FILE *f;
        char line[4096];
        bool success = true;

        f = fopen(fname, "rb");
        if (!f) {
                return 0;
        }

        /* just skip 1st line */
        if (!fgets(line, sizeof(line), f)) {
                success = false;
                goto done;
        }

        //while (!fgets(line, sizeof(line), f)) {
        while (fgets(line, sizeof(line), f)) {
                char *p;
                uint64_t addr, size, value;

                p = line;
                if (!file_get_value(p, &addr, 16)) {
                        continue;
                }
                p = file_skip_field(p); // go to 'size'
                if (!file_get_value(p, &size, 0)) {
                        continue;
                }
                p = file_skip_field(p); // go to 'type'
                p = file_skip_field(p); // go to 'rw/ro'
                p = file_skip_field(p); // go to 'name'
                p = file_skip_field(p); // go to 'description'
                p = file_skip_field(p); // go to 'default'
                if (!file_get_value(p, &value, 0)) {
                        continue;
                }
                /* we can ignore other fields, no need to skip further */

                /* we need cell address so strip OTP_BASE (if any) */
                if ((addr & 0x07F80000) == 0x07F80000) {
                        addr = (addr & 0xFFFF) >> 3;
                }

                success &= value_cb((uint32_t) addr, (uint32_t) size, value);
        }

done:
        fclose(f);

        return success;
}

int dump_partition_table(uint8_t *buf, size_t total_len)
{
        cmd_partition_table_t *table = (cmd_partition_table_t *)(buf);
        const size_t len = total_len - sizeof(cmd_partition_table_t);
        const uint16_t sector_size = table->sector_size;
        uint16_t offset = 0;

        if (len < sizeof(cmd_partition_table_t)) {
                printf("No partition table found!!\n");
                return 1;
        }

        printf("\n\nSector size: %u bytes \n", sector_size);

        printf("start  #sectors    offset       size        id      name\n\n");

        do {
                printf("0x%02x     0x%02x     0x%06x     0x%05x     0x%02x     %s\n",
                                table->entry.start_sector,
                                table->entry.sector_count,
                                table->entry.start_sector * sector_size,
                                table->entry.sector_count * sector_size,
                                table->entry.type,
                                &(table->entry.name.str));
                offset += sizeof(cmd_partition_entry_t) + (table->entry.name.len);
                table = (cmd_partition_table_t *)(buf + offset);
        } while(len > offset);

        return 0;
}

static cmd_partition_entry_t **get_available_partitions(uint8_t *part_count)
{
        int ret;
        int cnt = 0;
        int i, n = 0;
        size_t len;
        uint8_t *buf = NULL;
        unsigned int size = 0;
        uint16_t offset = 0;
        cmd_partition_table_t *table;
        cmd_partition_entry_t **partitions = NULL;

        ret = prog_read_partition_table(&buf, &size);
        if (ret) {
                fprintf(stderr, "read partition table failed: %s (%d)\n", prog_get_err_message(ret),
                                                                                                ret);
                goto done;
        }
        table = (cmd_partition_table_t *)(buf);
        len = size - sizeof(cmd_partition_table_t);

        if (len < sizeof(cmd_partition_table_t)) {
                printf("No partition table found!!\n");
                goto done;
        }

        // Count number of available partitions
        for (i = 0; i < (size - 4); i++) {
                if (strncmp((char *) &buf[i], "NVMS", 4) == 0) {
                        cnt++;
                }
        }
        *part_count = cnt;

        partitions = malloc(cnt * sizeof(cmd_partition_entry_t *));

        do {
                partitions[n] = malloc(sizeof(cmd_partition_entry_t) + table->entry.name.len);
                memcpy(partitions[n++], &table->entry,
                                        sizeof(cmd_partition_entry_t) + table->entry.name.len);

                offset += sizeof(cmd_partition_entry_t) + (table->entry.name.len);
                table = (cmd_partition_table_t *)(buf + offset);
        } while (len > offset);

done:
        if (buf) {
                free(buf);
        }
        return partitions;
}

bool is_valid_partition_id(nvms_partition_id_t id)
{
        int i;
        bool found = false;
        uint8_t part_count = 0;
        cmd_partition_entry_t **partitions = NULL;

        partitions = get_available_partitions(&part_count);

        if (!partitions) {
                fprintf(stderr, "no partitions found\n");
                return false;
        }

        for (i = 0; i < part_count; i++) {
                if (id == partitions[i]->type) {
                        found = true;
                }
                free(partitions[i]);
        }

        free(partitions);

        return found;
}

bool is_valid_partition_name(const char *name, nvms_partition_id_t *id)
{
        int i;
        int ret;
        bool found = false;
        uint8_t part_count = 0;
        cmd_partition_entry_t **partitions = NULL;

        partitions = get_available_partitions(&part_count);

        if (!partitions) {
                fprintf(stderr, "no partitions found\n");
                return false;
        }

        for (i = 0; i < part_count; i++) {
                ret = strcasecmp(name, (char *) &partitions[i]->name.str);
                if (!ret) {
                        *id = partitions[i]->type;
                        found = true;
                }
                free(partitions[i]);
        }

        free(partitions);

        return found;
}
