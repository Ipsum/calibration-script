// UF1.07.5.c Nov 12 2009. Major mods to decrease bubble sensitivity.
// Bug fixes for better fault recovery.
/* All code relevant to fast transient response is removed.
	If faulted, loop current goes to 4 ma, never below.
	Number of bad measurements allowed is 20 in Slow mode, 100 in Fast mode.
	Bad _meas counter is reset to zero when a good measurement is made rather
	than simply decremented.
	A Bad measurement is declared if the difference between the highest and
	lowest values in the twenty samples exceeds .5% of the TCur time.Line 162.
	Fault is activated if Flow is  > 125% of FS. Loop current  is > 20 ma
*/	
// Oct 14 09. Modified Electronic cal
// Feb 13. No changes to this file.
// UF1.07.2D.c Feb 10 09. These have better corrections and leave PWRDWN off to less distrube loopi.
// For debug of Rev 3 PCBs only. Do not ship.
// No K adjust allowed, Inc & Dec force flows.
// Any deviation from standard options must be made only in copies of these files, with appropriate 
//	identifirers. i.e. Ux107.1_pkp.x for say PKP special options.
// Derived from 1.07P_mcn 1/23/09

//	This source code is confidential to Clark Solutions, Hudson Ma
// and may not be used for any purpose without written consent from Clark Solutions.
//	Author:	Jack Zettler Teconex Inc

#ifndef __UF1c__
#define __UF1c__
#endif
#include "UF1.07.5.h"
#include	"UC1.07.5.h"
#include	"ufdefs.h"
#include "parameters.h"

//#define _TEN

bank1 	byte 						Enable_delay;
extern   bank1  byte 			Check;
extern	bank1 double			HFConst;
extern 	bank1 uint16 			Delay_ticks;
extern 	bank1 double			K, TCur;
extern	uint16					FS;			//Full scale for this pipe size
extern	bank1 byte				Size_ind, Bad_limit;
extern	bank1 byte				Resp,Pt;
extern 	bank1	double			Lasti;

const byte	Uf_init[7][2] = //Array of uf register addresses and their init values
{
	{REG1,PWIDTH},{REG5,LOOPCL},{REG6,LOOPCH},{REG12,LDELAY},
	{REG13,ANASAMPLEL},{REG14,ANASAMPLEH}, {REG15,PCYCL}
};
//     								  3/4     1.0	   1.5	  2.0	     3.0	      4.0        6.0	          8.0
const	uint16	Fs_G[8][2] = {{15,25},{30,50},{40,80},{60,120},{200,400},{500,1000}, {1000,2000}, {2000, 4000}};
const	uint16	Fs_L[8][2] = {{60,100},{115,200},{150,300},{225,575},{750,1500},{500,800}, {1000,2000}, {2000, 4000}};
//	Pipe sizes  				  3/4  1.0	1.5  2.0	 	  3.0	   4.0    6.0	   8.0
const double	K_init[8] = {.86, .92, 3.25, 3.26, 13.089, 29.6, 130.46, 373.1};	
const double	Tt[8] = {98, 98, 100, 100, 130, 160, 227, 283};	//Nominal Transit times
// Tt[8] is Tt for BoN tester	
const byte		Ptrig[8] = {0xE6,0xE2,0xE6,0xE6,0xE6,0xE6,0xE6,0xE6};		//PTRIG values
	
//Calibrate HF Clock and AGCs	
byte	ucal_ufo(void)
	{
		byte check = NO_ERROR;
		int		calc;
		uint16	hf1,hf2;
		
		PWRDWN = OFF;
		uset_reg(REG0, RESET_UFO);	//If no reset, last reg values are used
		uset_reg(REG0, UNSET_UFO);
		uagc(UP_DIR);
		HFConst = 1;							//Avoid div by 0
		uset_reg(REG15, HF_CAL );			//Set Hf cal bit,leave Pcycle bit
		INTF = OFF;								//Clear INTF flag	
		us_start(UP_DIR);						//Cal using up direction
		delay(TIMEOUT);
		if(!INTF)
			check = ERROR;
		else
			{
			TRISC = TRISC_IN;						//Set PortC for input
			CCP1CON = CCP1CON_DATA;				//Disble PWM while reading data					
			hf1 = (uf_read(REG6) << 8 | uf_read(REG5))*10;
			hf2 = (uf_read(REG8) << 8 | uf_read(REG7))*10;
			TRISC = TRISC_OUT;					//Restore PortC to output
			CCP1CON = CCP1CON_PWM;				//Renable PWM mode
			calc = hf2 -hf1;
			if(calc<0) { calc *= -1; }	//Set HFConst
			HFConst = (double)calc;		//Set HFConst
			}
		uset_reg(REG15, PCYCL);				//Reset HFcal
		if((HFConst > 1200) || (HFConst < 700))
			check = ERROR;			
		return(check);
}
// Writes data to selected UFO register	
void	uset_reg(byte add, byte data)
{
	CCP1CON = CCP1CON_DATA;
	TRISC = TRISC_OUT;			//Set PortC to output	
	PORTA = add;					//Set address
	TRISC = TRISC_OUT;	
	UFO_CS = ENABLED;				//Enable chip select	
	PORTC = data;					//Put data on bus
	UFO_WR = ENABLED;				//Strobe WR
	UFO_WR = DISABLED;
	UFO_CS = DISABLED;			//Raise CS
	CCP1CON = CCP1CON_PWM;		//Restore CCP1CON
}
// Routine to initiate action currently selected by uset_reg()



void us_start(byte direction)
{
	byte		dir_start, dir_en,etime;

	uset_reg(REG0, RESET_UFO);			
	dir_start = direction | START_UFO;
	dir_en = direction | EN_UFO;
	uset_reg(REG0,direction);			//Set direction bit
	etime = 2*(START_DELAY - 7);		//Don't ask	
	TMR1L = 0;
	while(TMR1L < etime);				//Consequence of no. of instr.
	uset_reg(REG0,dir_start);			//Set start bit
	etime = 0;
	while(etime < Enable_delay)
		etime++;
	uset_reg(REG0,dir_en); 				//Set enable bit
	asm("clrwdt");
}

// Returns UFO register data
byte	uf_read(byte add)
	{
	byte	rtrn;
	PORTA = add;					//Set address
	UFO_CS = ENABLED;				//Enable chip select
	UFO_RD = ENABLED;				//Strobe RD
	rtrn = PORTC;					//Put data away
	UFO_RD = DISABLED;
	UFO_CS = DISABLED;			//Raise CS
	return(rtrn);	
	}
// Returns transit times after reading registers

		
double us_save(void)
{
	int32	cnt;
	int16	hf1,hf2,h;
	double	delta, tt;
	
	TRISC = TRISC_IN;						//Set PortC for input
	CCP1CON = CCP1CON_DATA;				//Disble PWM while reading data		
	cnt = (uint32)uf_read(REG4) <<16;
	cnt |= uf_read(REG3) <<8;
	cnt |= uf_read(REG2);
	hf1 = (uf_read(REG6) << 8 | uf_read(REG5))*10;
	hf2 = (uf_read(REG8) << 8 | uf_read(REG7))*10;
	TRISC = TRISC_OUT;					//Restore PortC to output
	CCP1CON = CCP1CON_PWM;				//Renable PWM mode
	h = 2*(hf1-hf2);
	delta = (double)h/HFConst;
	tt = (cnt +delta)/(CLK_FREQ *(LOOPCL -1));
	asm("clrwdt");	
	return(tt);
}
// Initializes UFO, determines pipe size K factor & Units
void uf_init(void)
{
	byte 		i,size,fs,sregl,sregh;
	double	smarktime;
	uint16	sregs;	
	asm("clrwdt");	
	size = read_sw();						//Get switch setting
	Size_ind = size >> 5;				//3 bit pipe dia index
#ifdef _TEN
	Size_ind = 8;
#endif	
	K = load_eeprom_data(K_ADD);
	if(K <.5)								// First time?
		{
		K 	= K_init[Size_ind];			//K for this pipe size,Gal/min
		if(size & 0x01)					
			K *= 3.785;						//Asking for liters/gal
		write_eeprom_data(K_ADD, K);
	}
	fs = (size & 0x08) ? HI :LO;		//FS selection
	if(size & 0x01)
		FS = Fs_L[Size_ind][fs];		//Set FS Gal value to use.
	else
		FS = Fs_G[Size_ind][fs];
#ifdef _lowFS
	if(!fs)
		FS = _lowFS;
	else
		FS = _highFS;
#endif
	//Set response time and bad measurement limit to use.				
	Resp = (size & 0x10) ? FAST : SLOW;
	Bad_limit = (size & 0x10) ? BAD_LIMIT_FAST : BAD_LIMIT_SLOW;	
	Pt = Ptrig[Size_ind];		
	TRISC = TRISC_OUT;					//Enable data lines for output
	PWRDWN = OFF;							//Allow UFO to power up
	delay(5);
	uset_reg(REG0,RESET_UFO);			//Reset all
	uset_reg(REG0,UNSET_UFO);
	for(i = 0;i < MAXADD; i++)			//Non size dependent registers only
		uset_reg(Uf_init[i][0], Uf_init[i][1]);	//Traverse array of addresses and data
	TCur = Tt[Size_ind];						//Start with nominal Tt
	smarktime = .75*Tt[Size_ind];	
	Enable_delay = (byte)(smarktime/8); //6 us/timing loop
	sregs = (uint16)(smarktime*CLK_FREQ - 2);	//SMARK value
	sregl = (byte)(sregs & 0x00FF);
	sregh = (byte)(sregs >> 8);
	uset_reg(REG7,sregl);				//Set SMARKL
	uset_reg(REG8,sregh);				//Set SMARKH
	sregs = (uint16)(1.25*CLK_FREQ*Tt[Size_ind] - 2);	//SSPACE value
	sregl = (byte)(sregs & 0x00FF);
	sregh = (byte)(sregs >> 8);
	uset_reg(REG9,sregl);				//Set SSPACEL
	uset_reg(REG10,sregh);				//Set SSPACEH
	asm("clrwdt");	
}	


void uagc(byte dir)
{
	
	asm("clrwdt");	
	Check = NO_ERROR;
	uset_reg(REG11,REG11_RESET);	//Without this, a call to ustart_ufo() after
	uset_reg(REG11,PTRIG_AGC);		//an iduced measurement failure will fail continuously??
	INTF = OFF;							//Clear INTF flag	
	Delay_ticks = TIMEOUT;	
	us_start(dir | AGC_CAL);		//Start an AGC cal in passed direction 
	while(!INTF && Delay_ticks);	//Wait for ufo interrupt or time out
	if(!Delay_ticks || !INTF)
	 	Check = ERROR;					//Missed AGC
	uset_reg(REG11, Pt);
}


