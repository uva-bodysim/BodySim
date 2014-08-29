/****************************************************************************/
/* VECTDEFS.H: definitions from vectmath.h, separated for programs which    */
/* need to define vectors without loading the whole mess of definitions.    */
/* Copyright (c) 1999 by Joshua E. Barnes, Tokyo, JAPAN.                    */
/****************************************************************************/

#ifndef __VECTDEFS_H__
#define __VECTDEFS_H__

#if !defined(NDIM) && !defined(TWODIM) && !defined(THREEDIM)
#define THREEDIM                              /* supply default dimensions  */
#endif

#if defined(THREEDIM) || (NDIM==3)
#undef  TWODIM
#define THREEDIM
#define NDIM 3
#endif

#if defined(TWODIM) || (NDIM==2)
#undef  THREEDIM
#define TWODIM
#define NDIM 2
#endif

typedef float vector[NDIM];
typedef float matrix[NDIM][NDIM];

#endif
/* ! _vectdefs_h */
