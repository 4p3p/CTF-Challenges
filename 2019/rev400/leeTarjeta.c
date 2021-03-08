#include<stdio.h>
#include<mysql.h>
#include<stdlib.h>
#include<string.h>
void uso();
char* xor(char *,int*);
char *esab_encode(const unsigned char *,size_t,size_t *);
unsigned char *esab_decode(const char *,size_t,size_t *);
void build_decoding_table();
void esab_cleanup();
char *decode(char*,size_t);
char *encode(char*);

static char *server = "localhost";
static char *database = "db";

static int xkey[] = {0x73,0x75,0x70,0x33,0x72,0x73,0x33,0x63,0x75,0x72,0x33,0x68,0x34,0x64,0x72,0x63,0x30,0x64,0x33,0x64,0x6b,0x33,0x79,0x74,0x30,0x78,0x30,0x72,0x33,0x76,0x33,0x72,0x79,0x74,0x68,0x31,0x6e,0x67};
static char encoding_table[] = {'Z', 'Y', 'X', 'W', 'V', 'U', 'T', 'S',
                                'R', 'Q', 'P', 'O', 'N', 'M', 'L', 'K',
                                'J', 'I', 'H', 'G', 'F', 'E', 'D', 'C',
                                'B', 'A', 'a', 'b', 'c', 'd', 'e', 'f',
                                'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
                                'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
                                'w', 'x', 'y', 'z', '0', '1', '2', '3',
                                '4', '5', '6', '7', '8', '9', '+', '/'};
static char *decoding_table = NULL;
static int mod_table[] = {0, 2, 1};

int main(int argc, char **argv)
{
	char *user = *(argv+1);
	char *password = *(argv+2);
	if(argc<4)
	{
		uso();
		return 0xd34d;
	}
	if(strcmp("dump",*(argv+3))==0)
	{
		MYSQL *conn;
		MYSQL_RES *res;
		MYSQL_ROW row;
		conn = mysql_init(NULL);
		if (!mysql_real_connect(conn, server, user, password, database, 0, NULL, 0))
		{ 
			fprintf(stderr, "%s\n", mysql_error(conn));
			exit(1);
		}
		if (mysql_query(conn, "select * from encrypted_cards"))
		{
			fprintf(stderr, "%s\n", mysql_error(conn));
			exit(1);
		}
		res = mysql_use_result(conn);
		size_t s;
		printf("ID\tCard_Number\t\t\tValidation_Key\t\t\tExpiration_Date\t\tCCC_Code\t\tAmount_Limit\t\tDenominacion\t\tBlocked\n");
		while ((row = mysql_fetch_row(res)) != NULL)
			printf("%s\t%s\t%s\t%s\t\t%s\t\t\t%s\t\t%s\t\t%s \n", row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]);
		mysql_free_result(res);
		mysql_close(conn);
	}
	else if(strcmp("validate",*(argv+3))==0)
	{
		if(argc<5)
		{
			uso();
			exit(1);
		}
		MYSQL *conn;
		MYSQL_RES *res;
		MYSQL_ROW row;
		conn = mysql_init(NULL);
		if (!mysql_real_connect(conn, server, user, password, database, 0, NULL, 0))
		{ 
			fprintf(stderr, "%s\n", mysql_error(conn));
			exit(1);
		}
		char query[300]; 
		char *q1 = "select * from encrypted_cards where validation_key like \"%";

		if(strlen(*(argv+4))<15||strlen(*(argv+4))>16)
		{
			printf("El codigo de validacion consta de 16 bytes, pero, la fuerza bruta no es la solucion...\n");
			exit(1);
		}

		strcat(query,q1);
		strcat(query,encode(*(argv+4)));
		strcat(query,"%\"");

		if (mysql_query(conn, query))
		{
			fprintf(stderr, "%s\n", mysql_error(conn));
			exit(1);
		}
		res = mysql_use_result(conn);
		while ((row = mysql_fetch_row(res)) != NULL)
			if(atoi(row[0])==0x57)
				printf("ID: %s\t\nCARD(FLAG): %s\t\n\n", row[0],decode(row[1],28));
		mysql_free_result(res);
		mysql_close(conn);
	}
	else
	{
		uso();
		return 0xf4d3;
	}
	return 1337;
}

void uso(char **argv)
{
	printf("Uso: ./ejecutable dbuser dbpasswd modo-de-uso <codigo de validacion> \n\n\tModos de uso:\n\tdump: dumps encrypted database values\n\tvalidate: validates unencrypted secret password, then dumps the registers related to this account\n\n");
}

char* xor(char* str, int* key)
{
	char *ret = (char *)calloc(strlen(str),sizeof(char));
	char **r=ret;
	do
	{
		*ret=*str^(char)*key;
		*(ret++);
	} while ((*(str++)&&*(key++)));
	return r;
}

char *esab_encode(const unsigned char *data,
                    size_t input_length,
                    size_t *output_length) {
 
    *output_length = 4 * ((input_length + 2) / 3);
 
    char *encoded_data = malloc(*output_length);
    if (encoded_data == NULL) return NULL;
 
    for (int i = 0, j = 0; i < input_length;) {
 
        u_int32_t octet_a = i < input_length ? (unsigned char)data[i++] : 0;
        u_int32_t octet_b = i < input_length ? (unsigned char)data[i++] : 0;
        u_int32_t octet_c = i < input_length ? (unsigned char)data[i++] : 0;
 
        u_int32_t triple = (octet_a << 0x10) + (octet_b << 0x08) + octet_c;
 
        encoded_data[j++] = encoding_table[(triple >> 3 * 6) & 0x3F];
        encoded_data[j++] = encoding_table[(triple >> 2 * 6) & 0x3F];
        encoded_data[j++] = encoding_table[(triple >> 1 * 6) & 0x3F];
        encoded_data[j++] = encoding_table[(triple >> 0 * 6) & 0x3F];
    }
 
    for (int i = 0; i < mod_table[input_length % 3]; i++)
        encoded_data[*output_length - 1 - i] = '=';
 
    return encoded_data;
}

unsigned char *esab_decode(const char *data, size_t input_length, size_t *output_length) {
    if (decoding_table == NULL) build_decoding_table();
 
    if (input_length % 4 != 0) return NULL;
 
    *output_length = input_length / 4 * 3;
    if (data[input_length - 1] == '=') (*output_length)--;
    if (data[input_length - 2] == '=') (*output_length)--;
 
    unsigned char *decoded_data = malloc(*output_length);
    if (decoded_data == NULL) return NULL;
 
    for (int i = 0, j = 0; i < input_length;) {
 
        u_int32_t sextet_a = data[i] == '=' ? 0 & i++ : decoding_table[data[i++]];
        u_int32_t sextet_b = data[i] == '=' ? 0 & i++ : decoding_table[data[i++]];
        u_int32_t sextet_c = data[i] == '=' ? 0 & i++ : decoding_table[data[i++]];
        u_int32_t sextet_d = data[i] == '=' ? 0 & i++ : decoding_table[data[i++]];
 
        u_int32_t triple = (sextet_a << 3 * 6)
        + (sextet_b << 2 * 6)
        + (sextet_c << 1 * 6)
        + (sextet_d << 0 * 6); 
 
        if (j < *output_length) decoded_data[j++] = (triple >> 2 * 8) & 0xFF;
        if (j < *output_length) decoded_data[j++] = (triple >> 1 * 8) & 0xFF;
        if (j < *output_length) decoded_data[j++] = (triple >> 0 * 8) & 0xFF;
    }
 
    return decoded_data;
}
 
void build_decoding_table() { 
    decoding_table = malloc(256);
 
    for (int i = 0; i < 64; i++)
        decoding_table[(unsigned char) encoding_table[i]] = i;
}

void esab_cleanup() {
    free(decoding_table);
}

char* decode(char *string,size_t t){
	size_t s = 0;
	char* rv = xor(esab_decode(string,t,&s),xkey);
	if(rv[s]=='d'||rv[s]=='0'||rv[s]=='r'||rv[s]=='3'||rv[s]=='p')
		rv[s]='\0';
	return rv;
}

char *encode(char *string)
{
	size_t s;
	char *rv = esab_encode(xor(string,xkey),strlen(string),&s);
	rv[s-2]='\0';
	return rv;
}