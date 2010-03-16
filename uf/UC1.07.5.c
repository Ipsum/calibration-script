// UC1.07.5.c Dec 14 2009. For use in Precal Station only.
// Bug fixes for better fault recovery.
// Oct 14 09. Derived from UC1.07.3D.C. Modified Electronic cal
/* All code relevant to fast transient response is removed.
	If faulted, loop current goes to 4 ma, never below.
	Number of bad measurements allowed is 20 in Slow mode, 100 in Fast mode.
	Bad _meas counter is reset to zero when a good measurement is made rather
	than simply decremented.
	A Bad measurement is declared if the difference between the highest and
	lowest values in the twenty samples exceeds .5% of the TCur time.Line 162.
	Fault is activated if Flow is  > 125% of FS. Loop current  is > 20 ma
*/	

//	This source code is confidential to Clark Solutions, Hudson Ma
// and may not be used for any purpose without written consent from Clark Solutions.
//	Author	Jack Zettler Teconex Inc

//#ifndef __UC1c__
//#define __UC1c__
//#endif

#include "ufdefs.h"
#include	<stdio.h>
#include	<stdlib.h>
#include	<math.h>
#include	"UC1.07.5.h"
#include	"UF1.07.5.h"
#include "parameters.h"
#include	<pic.h>    	


#define	_FLT			//Compile for Fault option
//#define	_DIR		//Compile for Direction option 


bank1 byte				Check;			//Return values
bank1 uint16			Delay_ticks;	//	Delay_ticks;
bank1	double			K, TCur;			//Flow constant (Path Length/2*cos(angle)),Tt
uint16					FS;				//Full scale for this pipe size
bank1	double			Tup, Tdwn;		//Up and down transit times
bank1	double			HFConst;			//D-Flow clock multiplier
bank1 double			M1,B1;			//Electronic cal coefficients, Dz correction
bank1	byte				Resp;				//Selected response time
bank1	byte				Size_ind, Pt;	//Pipe size, Pretrig value
bank1 byte				Bad_FS;			//Current number of over ranger measurements
bank1 byte				Bad_meas;		//Current number of bad measurements
bank1 byte				Bad_limit;		//Allowed number of bad measurements
bank1 byte				Dir, Do_dz;		//Flow direction
bank1	double			Lasti,Flow;		//Previous loop i,current Flow
bank1	double			Cur;				//Scratch variable
bank1 double			Dz;				//Delta Tt at zero flow
bank2 double			Tu[MAX];			//Array of Up transit times
bank3 double			Td[MAX];			//Array of Down transit times
extern const double	Tt[8];			//Nominal transit times
		


//HS,WDT off,Code protect Off,ICSP Enabled,Flash Mem write enabled, 		      
__CONFIG(UNPROTECT & WDTDIS &HS  &LVPDIS &BORDIS &PWRTEN &DEBUGEN);


main()
{
	double 		last_Flow,loopi, dc;
	double 		accum ; 
	byte			i,j,k,d;
	byte			loops, bad_limit;

	init873();						//Init processor
	if(!TO)
		{
		asm("clrwdt");				//Clear Watch dog timer,resets TO
		blink(50);					//Indicate a WDT timeout
		}
#ifdef K_auto
	write_eeprom_data(K_ADD, K_auto);	
	write_eeprom_data(DZ_ADD, DZ_auto);
#endif	
//	write_eeprom_data(M1_ADD,.041);
	M1 = load_eeprom_data(M1_ADD);
	B1 = load_eeprom_data(B1_ADD);
	Dz = load_eeprom_data(DZ_ADD);
	M1 = (M1 < .01) ? .041 : M1;	//Set to nominal if first time	
	uf_init();							//Initialize the D-Flow ASIC
	reset_opts();						//Select reset options
	accum = 0;
	cal_ufo();
	get_times();
	TCur = (Tup+Tdwn)/2;
	FAULT = DISABLED;
#ifdef _DZ
	Dz = 0;
	Do_dz = YES;
#endif
	dc = M1*4.0+ B1 +.002;				//Calculate duty cycle
	dc = (dc > .95) ? .95 : dc;
	set_dc(dc);	
	loops = FAST;							//Start first update at 2 sec response
	bad_limit = BAD_LIMIT_FAST;

						//Do HF Const calibration
			
	
/*
Measurement loop. Average of a number of measurements set by the Resp variable, read from
SW3, are made with .25 sec delay between each measurement. Loop current is update at a rate equal to
Resp * .25 seconds. If Resp is set to S, (Slow) update rate is 20 * .125 or 5 secs. If set to F, Fast)
Update rate is 8 * ..25 or 2 seconds
*/

	while(1)
	{
		do
		{
		while(INC || DEC)				//Changed from do{} to not add delay(100)
			{
			if(INC)
					K *= 1.002;			//Inc K by .2%
			if(DEC)
					K /= 1.002;			//Dec K by .2 %
			delay(100);	
			}
		if(!CAL_READ)
			{
			delay(20);
			while(!CAL_READ)	
				asm("clrwdt");
			Delay_ticks = 2000;
			while(Delay_ticks && !INC)
				asm("clrwdt");
			if(INC)
				{	
				write_eeprom_data(K_ADD, K);
				blink(100);					//Show that K was saved
				}
			while(INC)
				asm("clrwdt");				
			delay(20);						//Wait .02  sec
			}
			delay(84);
			get_times();						//Make a measurement
			if(j < MAX  && Check != ERROR)//Collect MAX good measurements
				{
				Tu[j] = Tup;
				Td[j] = Tdwn;
				if ((Flow > 1.25*FS) && (Bad_FS < bad_limit))//Error if > 1.25 Full Scale
					Bad_FS++;
				else 
					Bad_FS = 0;;				//Reset when back in range
				j++;
				}
			if((Check == ERROR) && (Bad_meas < bad_limit))
	 				Bad_meas++;					//Inc bad measure cntr,don't wrap
			 if((Check == NO_ERROR) && (j == MAX))
				{
				for(j = 0; j < MAX; j++)	//Sort high to low
					{
					Cur = Tu[j];				//Sort Tup times
					for(k = j; k < MAX; k++)
						{
						if(Tu[k] > Cur)
							{
							Tu[j] = Tu[k];
							Tu[k] = Cur;
							Cur = Tu[j];
							}
						}
					}
				for(j = 0; j < MAX; j++)	//Sort high to low
						{
						Cur = Td[j];			//Sort Tdwn times
						for(k = j; k < MAX; k++)
							{
							if(Td[k] > Cur)
								{
								Td[j] = Td[k];
								Td[k] = Cur;
								Cur = Td[j];
								}
							}
						}
				Tup = Tdwn = 0;
				for(j = OFFSET; j < (MAX - OFFSET); j++)
					{
					Tup 	+= Tu[j];			//Accumulate central times
					Tdwn 	+= Td[j];
					k = j;
					}
				Tup /= (MAX - 2*OFFSET);	//Tup to use for Flow calculation
				Tdwn /= (MAX - 2*OFFSET);	//Tdwn to use for Flow calculation
//				TCur = (Tup + Tdwn)/2;		//Current Tt
				j = 0;						
				if(((Td[0] - Td[MAX-1])< .005*TCur) && ((Tu[0] - Tu[MAX-1])< .005*TCur))
					{					
					if(Do_dz == YES)
						{
						cal_dz(&d);
						Flow = 0;
						}
					else
						Flow = K*1e6*(1/(Tdwn+Dz) - 1/(Tup-Dz));			//Flow in gal/min or liter/min
					accum += Flow;				//Tally good measurement
					i++;							//Continue
					j = 0;
					if ((Bad_meas > 0) && (Check != ERROR))
						Bad_meas--;					//Decrement Bad countert bad cntr
					TCur = (Tup + Tdwn)/2;		//Current Tt						
					}
				else if(Bad_meas < bad_limit)
					Bad_meas++;
				}								
			asm("clrwdt");	
			}
		while((i< loops) && (Bad_meas !=bad_limit)&& (Bad_FS !=bad_limit));
		 if(Bad_meas ==0 && Bad_FS ==0)
			FAULT = DISABLED;				
		if((Bad_meas ==bad_limit) || (Bad_FS ==bad_limit))
			{
			#ifdef _FLT		 			
				FAULT = ENABLED;		//Give Fault output if Fault option
			#endif
			if(Bad_meas ==bad_limit)//Never report less than 4.0 ma
				{							//unless	fault is overrange
				loopi = 4.0;					
				cal_ufo();				//Try to recover
				get_times();
				TCur = (Tup+Tdwn)/2; //If there was a good AGC, this willl be the best 
				Bad_meas = 0;			//current average transit time.
				loops = FAST;			//For 2 sec recovery
				bad_limit = BAD_LIMIT_FAST;
				}
			}
		else
			{
			Flow = fabs(accum/i);				//Running average				
			last_Flow = Flow;	
			loopi = 4.0 + 16*Flow/FS;				//Set loopi for measured Flow
			loopi = (loopi < 4.25) ? 4.0 :loopi;//For minimum turn down Flow
			loops = Resp;								//For selected recovery	
			bad_limit = Bad_limit;										
			}			
		Lasti = loopi;
		dc = M1*loopi + B1 +.002;				//Calculate duty cycle
		dc = (dc > .95) ? .95 : dc;
		set_dc(dc);
		i = j = 0;
		accum = 0;
		}
}				//End main()

void		get_times(void)
{
	Check = NO_ERROR;
	INTF = OFF;		
	Delay_ticks = TIMEOUT;
	Tup = Tdwn = 0.0;
	us_start(DWN_DIR);					//us_start() turns PWRDWN off
	while((!INTF) && Delay_ticks);	//Wait for ufo interrupt or time out
	if(!Delay_ticks)
		{
		uset_reg(REG0,RESET_UFO);
		uset_reg(REG0,DWN_DIR);
		uset_reg(REG11,(0x7F|Pt));	//Without this, a call to ustart_ufo() after
		uset_reg(REG11,(0xC0|Pt));	//an iduced measurement failure will fail continuously??
		uset_reg(REG15,PCYCL);		
	 	Check = ERROR;						//Bad measurement
	 	}
 	else
	 	{
		Tdwn = us_save();						//us_save() turns PWRDWN ON
		uset_reg(REG0,(RESET_UFO | DWN_DIR));
		uset_reg(REG0,DWN_DIR);
		uset_reg(REG15,PCYCL);
		delay(1);								//Timefor VX to recover
		INTF = OFF;
		Delay_ticks = TIMEOUT;
		us_start(UP_DIR);					//us_start() turns PWRDWN OFF
		while(!INTF && Delay_ticks);	//Wait for ufo interrupt or time out
		if(!Delay_ticks)
			{
			uset_reg(REG0,RESET_UFO);
			uset_reg(REG0,UP_DIR);
			uset_reg(REG11,(0x7F|Pt));	//Without this, a call to ustart_ufo() after
			uset_reg(REG11,(0xC0|Pt));	//an iduced measurement failure will fail continuously??
			uset_reg(REG15,PCYCL);		
	 		Check = ERROR;						//Bad measurement
	 		}
	 	else
	 		{
			Tup = us_save();
			uset_reg(REG0,(RESET_UFO | UP_DIR));
			uset_reg(REG0,UP_DIR);
			uset_reg(REG15,PCYCL);				
			}
		}
		if((Tdwn < .85*Tt[Size_ind]) || (Tup < .85*Tt[Size_ind]) ||(Tdwn > 1.15*Tt[Size_ind]) || (Tup > 1.15*Tt[Size_ind]))
			Check = ERROR;
		 if((Tdwn < .995*TCur) || (Tup < .995*TCur) ||(Tdwn > 1.005*TCur) || (Tup > 1.005*TCur))
			{
			Check = ERROR;
			if(FAULT == DISABLED)
					TCur = (Tup + Tdwn)/2;
			}
	#ifdef _DIR						//Direction option
		if(Tup >=Tdwn)
			FAULT = DISABLED;
		else if( (Tup < Tdwn) && (Lasti > 4.4))//Don't report unless in range
			FAULT = ENABLED;
	#endif
}	

void cal_dz(byte *g)
{
Dz+ = Tup -Tdwn;
++ *g;
if(*g >= 19)
	{
	Dz/= 40;					//Dz must be less for small pipe sizes.			
	if((fabs(Dz) > .002)|| ((Size_ind < 4)&& (fabs(Dz) > .002)))
		{
		FAULT = ENABLED;
		while(1)
			asm("clrwdt");		
		}
	else
		{
		write_eeprom_data(DZ_ADD, Dz);
		write_eeprom_data(JUNK_ADD, 1);
		blink(100);					//Show that K was saved	
		Do_dz = NO;						
		}
	}
}

// Sets PWM duty cycle for loop current set point		
void	set_dc(double dc)						//dc is fractional duty cycle
	{
	uint16	dcr;
	double 	dcrd,id;
	double	*iptr;
	double	rem;
	
	TRISC = TRISC_OUT;
	dcrd = dc *(PR2_INIT +1)*4;
	iptr = &rem;
	id = modf(dcrd, iptr);			//Determine fraction to round to closest int value
	if(id >= .5)
		rem++;	
	dcr = (uint16)(rem);
	CCPR1L = (byte)(dcr >>2);				//MSB
	CCP1CON = 0x0C | (byte)(dcr <<4); 	//LSBs plus enable PWM
	}

void	cal_ufo()
	{
	double	dc;
	
	dc = M1*4.0 + B1 +.002;		
	set_dc(dc);						//Show 4 ma while calibrating
	do									//Do HF calibration
		{
		Check = ucal_ufo();
		if( Check == ERROR)	//Cal UFO
			{
			FAULT = ENABLED;	//If either option
			delay(500);
			}
		}
	while (Check == ERROR);
	}	
	
/*	This routine determines the slope and offset coefficients for the electronic calibration.
	These are determined from a two point calibration at 4 and at 20 ma.
*/

void	cal_416e(void)	
	{
		static double		dc4;
		static double		dc20;			//Duty cycle for 4 and 20 ma
		
		PWRDWN = OFF;						//Power UFO while calibrating @4 ma
		dc4 = .17;							//Nominal dc for 4 ma
		delay(50);							//Avoid switch bounce
		while(!CAL_READ);		
		while(CAL_READ)
			{
			set_dc(dc4);
			while(!INC && !DEC && CAL_READ)	//Wait for a button push
				asm("clrwdt");					//Clear Watch dog timer
			if(INC)
				dc4 += CORR;				//Increase dc4
			if(DEC)
				dc4 -= CORR;				//DEcrease dc4
			get_times();
			delay(84);					
			}
		while(!CAL_READ)					//Wait till button is released
			asm("clrwdt");					//Clear Watch dog timer
		delay(100);							//Avoid switch bounce		
		dc20 = .825;						//Nominal dc for 20 ma
		while(CAL_READ)
			{
			set_dc(dc20);
			while(!INC && !DEC && CAL_READ)	//Wait for a button push
				asm("clrwdt");					//Clear Watch dog timer				
			if(INC)
				dc20 += CORR;				//Increase dc20
			if(DEC)
				dc20 -= CORR;				//Decrease dc20
			get_times();
			delay(84);							//Simulate measurement	
			}
		while(!CAL_READ);					//Wait till button is released
	
// Now have necessary data to determine linear coefficients
		M1 = (dc20 - dc4)/(I20- I4);
		M1*=  1.009;
		B1 = dc4-M1*I4;					//Increase M1 for lessenes dc during measurements 
		write_eeprom_data(M1_ADD, M1);
		write_eeprom_data(B1_ADD,B1);
		write_eeprom_data(JUNK_ADD, 1);
		set_dc(dc4 +.00217);					;//Return to lower dc
	}
		

byte	read_sw(void)								//Return value of option switch
	{
	byte	rtrn;
	TRISA = TRISA_READ;
	TRISC = TRISC_IN;								//Set to output to read switch
	CAL_READ = ENABLED;							//Low to read	
	rtrn = PORTC;
	CAL_READ = DISABLED;							//Reset
	TRISA = TRISA_RUN;							//Set to run config
	return(rtrn);
	}

void reset_opts()				//Gets Reset options.

// If CAL is pressed when Reset is released,then a constant AGC is done.

{
	
	if(!CAL_READ)					//Do AGC
		{
		delay(100);					//Bounce
		while(!CAL_READ)
			asm("clrwdt");			//Clear Watch dog timer
		while(1)
			{
			uagc(UP_DIR);			//Used to view first echo strength
			delay(100);
			uagc(DWN_DIR);
			delay(100);
			} 	
		}
/*
	if(INC && !DEC)
		{
		delay(100);					//Bounce
		while(INC)
			asm("clrwdt");			//Clear Watch dog timer
		write_eeprom_data(K_ADD, 0);	//Force K to load for this pipe size
		write_eeprom_data(JUNK_ADD, 1);
		blink (50);
		}
*/
}	
	

//Routine to blink fault light at passed rate
void		blink(uint16 period)
	{
		byte i;
		for(i = 0; i < 8; i++)
		{
			FAULT = ENABLED;	//Blink FAULT
			delay(5);
			FAULT =DISABLED;
			delay(period);
			if(!CAL_READ)
				break;
		}
	}
//Initialize the PIC16FL873A
void	init873(void)
{

PORTB 		=	0x3B;				//Raise UFO CS,Wr,Rd,Pwr on
TRISB    	=  TRISB_ALL;
PWRDWN		=	ON;				//Power UFO down	
TRISC    	=  TRISC_IN;		//*3_25_08
TRISA    	=  TRISA_RUN;
ADCON0  	 	=  ADCON0_INIT;	//See .h file
ADCON1   	=  ADCON1_INIT;
T1CON    	=  T1CON_INIT;	
T2CON			=  T2CON_INIT;
OPTION		=  OPTION_INIT;
INTCON   	=  INTCON_INIT;
CCP1CON 		= 	CCP1CON_PWM;
TMR1IE		= ON;



//   All other register power up with 0X00 which disables all functions
//   and interrupts. These register will be addressed from the program as
//   needed.
PCON  =   0x03;	     	//Set these pwr up and brown out flags after pwr up.
TMR1L = TMR1L_SET_1MS;		
TMR1H	= TMR1H_SET_1MS;
TMR1ON = ON;            //TMR1 on
PR2	= PR2_INIT;			//Set PWM freq
TMR2ON = ON;            //TMR2 on
}
//					End of init873()


//Services TMR1 interrupts only
void interrupt isr(void) 
{

 if(TMR1IF && TMR1IE )			//Timer 1 interrupt
   {
	TMR1ON   =   OFF;				//Stop while reloading
   TMR1L = TMR1L_SET_1MS;		//Load Lo byte
   TMR1H = TMR1H_SET_1MS;		//Load Hi byte
    if (Delay_ticks > 0)		//Don't wrap
      Delay_ticks--;				//For delay timer
   TMR1IF   =   OFF;				//Reset IF flag
   TMR1ON = ON;					//Turn timer back on.
   }	   	
}

// Pause program execution for passed number of Tmr1 interrupts
//	 (1 ms per interrupt)
void   delay(uint16 ticks)  
{
		
	TMR1ON = OFF;						//Turn off timer while loading
	Delay_ticks = ticks;         	//Reset interrupts counter
	TMR1IF = OFF;						//Reset Tmr1 interrupt flag
	TMR1L = TMR1L_SET_1MS;      	//Load Lo byte
	TMR1H = TMR1H_SET_1MS;			//Loa Hi byte
	TMR1ON = ON;               	//Turn on timer 1
while (Delay_ticks > 0)      	//Delay_ticks is decremented in isr()
		asm("clrwdt");					//Keep WDT off
	TMR1ON = ON;
}
//				End of delay()
// Reads a double from the passed address
double	load_eeprom_data(byte d_add)
	{
	byte	i;
	byte *ptr;	
	double rtrn;
	
	ptr = (byte*)&rtrn;
	for(i= 0; i<4; i++) 
		{
		*ptr = eeprom_read(d_add);
		ptr++;
		d_add++;
		}
	return(rtrn);
	}
// Writes a double to the passed address
void	write_eeprom_data(byte d_add, double d_data)	
	{
	byte i;
	byte *ptr = (byte *) (&d_data);

	for(i = 0; i<4; i++)
	{
		EEIF = OFF;
		eeprom_write(d_add, *ptr);
		ptr++;
		d_add++;
		asm("clrwdt");
		while(!EEIF);
	}
}

