// UC1.07.5.h Dec 11 2009. No changes from UC1.07.4.h
/* All code relevant to fast transient response is removed.
	If faulted, loop current goes to 4 ma, never below.
	Number of bad measurements allowed is 20 in Slow mode, 100 in Fast mode.
	Bad _meas counter is reset to zero when a good measurement is made rather
	than simply decremented.
	A Bad measurement is declared if the difference between the highest and
	lowest values in the twenty samples exceeds .5% of the TCur time.Line 162.
	Fault is activated if Flow is  > 125% of FS. Loop current  is > 20 ma
*/	
//  Oct 14 09. Modified Electronic cal
// Feb 13. No changes to this file.
// UC1.07.2D.h Feb 10 09. These have better corrections and leave PWRDWN off to less distrube loopi.
// For debug of Rev 3 PCBs only. Do not ship.
// No K adjust allowed, Inc & Dec force flows.
// Any deviation from standard options must be made only in copies of these files, with appropriate 
//	identifirers. i.e. Ux107.1_pkp.x for say PKP special options.

//	This source code is confidential to Clark Solutions, Hudson Ma
// and may not be used for any purpose without written consent from Clark Solutions.
// Clark Solutions US Flow meter
// Author: Jack Zettler Teconex inc

#include <pic.h>

void		interrupt isr(void);						//Single interrupt service
void		init873(void);								//Initializes controller
void		delay(uint16);								//General purpose program delay
void		cal_ufo(void);								//Calibrate UFO only	
void		cal_416e(void);							//Calibrate 4-20 ma loop
void 		cal_dz(byte *g);							//Get a Dz	
void		get_times(void);	//Get times
void		set_dc(double dc);						//Set duty cycle
byte		read_sw(void);								//Read option switch
void		blink(uint16 period);					//Blink Fault LED	
double	load_eeprom_data(byte d_add);			//Retrieve EEPROM data
void		write_eeprom_data(byte d_add, double d_data);//Write data to EEPROM	
void		reset_opts(void);

#define		BAD_LIMIT_FAST	20		//Number of bad measurements before fault
#define		BAD_LIMIT_SLOW	100	//Number of bad measurements before fault
#define		FAST				1		//*5/5/08
#define		SLOW				5		//*5/5/08
#define		MAX				20
#define		OFFSET			5
//    Status definition

#define	PB(adr,bit)		@((unsigned)(&adr)*8 + (bit))


static bit   PWMO    	PB(PORTC,2);   	//PWM out
//EEDATA Adresses
//#define	M1_ADL		0x00		//Slope for dc calculation
#define	M1_ADD		0x00			//Slope for dc calculation
#define	B1_ADD		0x04			//Offset for dc calculation
#define	K_ADD			0x08			//K 
#define	DZ_ADD		0x0C			//Store DZ
#define  JUNK_ADD		0x40        //Protects eeprom from accidential writes?
#define	CORR			.0001
#define	I4				4.00			//Actual current at 5 ma
#define	I20			20.0			
#define	CLK_FREQ		7.3728		//MHz	
#define	GAL			0xFF	
// TRIS Assignments 

#define TRISA_RUN    0XC2	//Cal input, Address and Switch outputs
#define TRISA_READ	0xC0	//A1 set to output to read switch.
#define TRISB_ALL    0XC1	//Port B is Int input,out on 2:5, RB.6,.7 for ICSP
#define TRISC_IN	   0XFF	//Port C when reading UFO registers
#define TRISC_OUT    0X00	//Port C when writing UFO and for PWM,latch set
#define TRISC_PWM		0xFB	// D2 will be the PWM output
#define TRISC_LATCH 	0xFD;
//PortB assignments
static bit   UFO_INT		PB(PORTB,0);   //UFO int
static bit   FAULT		PB(PORTB,1);   //FAULT Latch En
static bit   PWRDWN		PB(PORTB,2);   //UFO Power down
static bit   UFO_WR		PB(PORTB,3);   //UFO write
static bit   UFO_RD		PB(PORTB,4);   //UFO read
static bit   UFO_CS     PB(PORTB,5);   //UFO chip select
static bit   SPSW		   PB(PORTA,0);   //Analog switch control
static bit   CAL_READ	PB(PORTA,1);  	//Cal request or read switch.
static bit   ADD0			PB(PORTA,2);   //Cal inc dc
static bit   ADD1		   PB(PORTA,3);   //Cal dec dc
static bit   INC			PB(PORTB,7);   //Cal inc dc	//Added for Ecal via Prog Conn
static bit   DEC		   PB(PORTB,6);   //Cal dec dc
//Port C is only bi-directional data

//Register initialization defines
#define  INTCON_INIT		0xC0 	//No interrupts enabled
#define  ADCON0_INIT		0x80	//FOSC/32,Chan 0, A/D off 
#define  ADCON1_INIT		0x86 	//All I/O
#define  T1CON_INIT 		0x00 	//Prescale= 1:1,Osc off, Fosc/4 clk,TMR1ON = Off
#define  T2CON_INIT 	 	0x00 	//Prescale= Postscale = 1:1, TMR2 Off
#define  OPTION_INIT 	0x8E 	//BO B pullups,TMR0 Focs/4,prescale = 1:64,WDT
										//Int on falling edge
#define	CHAN0				0x01	//Chan 0
#define	CCP1CON_DATA	0x00	//Disable PWM
#define	CCP1CON_PWM		0x0C	//Enable PWM, LSBs are 0
#define	EECON1_INIT		0x00	//Disable all EEPROM Reads/Writes

//Module defines
#define	TMR1L_SET_1MS		0xCE	//TMR1 lower byte
#define	TMR1H_SET_1MS		0xF8	//TMR1 High byte. Gives 1 ms period
#define	TMR1L_SET_1US		0xF8	//TMR1 lower byte
#define	TMR1H_SET_1US		0xFF	//TMR1 High byte. Gives 1 us period
#define	PIE1_INIT			0x01	//Allow timer1 ints
#define	PR2_INIT 	 		253   //Set PWM period to 10KHz //*Oct 31
#define	PWM_OFF				0x00	//Disabple PWM mode
#define	PWM_ON				0x0C	//Enables PWM

