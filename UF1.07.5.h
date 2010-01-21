// UF1.07.5.h Dec 11 2009. No changes from UF1.07.4.h
// UF1.07.4.h Oct 20 2009. Major mods to decrease bubble sensitivity.
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
// For release of Rev 3 PCBs only. Do not modify.
// No K adjust allowed, Inc &Dec force flows.
// Any deviation from standard options must be made only in copies of these files, with appropriate 
//	identifirers. i.e. Ux107.1_pkp.x for say PKP special options.

//	This source code is confidential to Clark Solutions, Hudson Ma
// and may not be used for any purpose without written consent from Clark Solutions.
// Clark Solutions US Flow meter
// Author: Jack Zettler Teconex inc

#ifndef __UF1h__
#define __UF1h__

#include <pic.h>
#include "ufdefs.h"

void 		uf_init(void);		//Added 4-7-08
void		uset_reg(byte add, byte data); 
void 		us_start(byte direction);
double 	us_save(void);
byte		ucal_ufo(void);
byte		read_reg0(void);		//Debug only
byte		uf_read(byte add);
void 		uagc(byte dir);

	
#define	MAXADD		7
#define	PWIDTH		0x02		//Excitation pulse = 1 REFCLK
#define	LOOPCL		0x05		//Do 14 loops
#define	LOOPCH		0x00
#define	LDELAY		0x01		//Measure to 2nd zero crossing
#define	START_DELAY	4			//??4
#define	PCYCL			0x00		//POWERCYCLE on
#define	RESET_UFO	0x80		//Bit 7 resets UFO
#define	UNSET_UFO	0x00
#define	UP_DIR		0x04		//Swapped to agree with D-Flow
#define	DWN_DIR		0x08
#define	START_UFO	0x01
#define	EN_UFO		0x02
#define	HF_CAL		0x02
#define	AGC_CAL		0x40
#define	AGC_SET		0x40		//Resets SMARK,SSPACE,ANSAMPLE cntrs,AGC= 1/2
#define	AGC_UNSET	0xC0		//Remove cntr rese, leave AGC = 1/2
#define	PT_RESET		0x7F		//Resets SMARK,SSPACE,ANSAMPLE only
#define	PT_UNSET		0xC0		//Reoves cntr reset only
#define	REG0			0xC3
#define	REG1			0xC7
#define	REG2			0xCB
#define	REG3			0xCF
#define	REG4			0xD3
#define	REG5			0xD7
#define	REG6			0xDB
#define	REG7			0xDF
#define	REG8			0xE3
#define	REG9			0xE7
#define	REG10			0xEB
#define	REG11			0xEF
#define	REG12			0xF3
#define	REG13			0xF7
#define	REG14			0xFB
#define	REG15			0xFF
#define	REG_TEST		0x40	//Set to read registers 0. 13. 14	
#define	TIMEOUT			5		//Wait 1 ms for ufo interrupt


//	Pipe dependent parameters
// For 1.5 in pipe
#define	ANASAMPLEL	0x4B		//~ 10 us
#define	ANASAMPLEH	0x00
#define	PTRIG_AGC	0xFF
#define	REG11_RESET	0x00

#endif
