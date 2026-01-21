# Równania

$$
\Delta u(n) = u(n) - u(n - 1) \\
\Delta u(n) = k_p \left[ \Delta e(n) + \frac{T_p}{T_i} \sum_{k=0}^{n} e(k) + \frac{T_d}{T_p} \Delta e(n) \right]
$$

Gdzie:

$u(n)$ - zmiana sygnału sterującego \
$e(n)$ - uchyb regulacji \
$k(p)$ - wzmocnienie regulatora \
$T_p$ - okres próbkowania [s] \
$T_i$ - czas zdwojenia [s] \
$T_d$ - czas wyprzedzenia [s]

$$
\frac{dT(t)}{dt} = \frac{1}{C_{total}}u(t) - h* \left[ T(t) - T_{amb} \right]
$$

Gdzie:

$C$ - pojemność cieplna $\left[\frac{J}{K}\right]$ \
$u(t)$ - sygnał sterujący \
$h$ - współczynnik strat ciepła do otoczenia $\left[ \frac{W}{K} \right]$ \
$T_{amb}$ - temperatura otoczenia $\left[^oC\right]$ \
$T(t)$ - aktualna temperatura układu $[^oC]$

$$
T(n+1) = T(n) + \frac{\Delta t}{C} u(n) - h * \left[ T(n) - T_{amb} \right]
$$
