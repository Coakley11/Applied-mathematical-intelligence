"""Cryptography — modular arithmetic and toy RSA."""

import math

import numpy as np
import streamlit as st


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    r = int(math.isqrt(n))
    for i in range(3, r + 1, 2):
        if n % i == 0:
            return False
    return True


def crypto_rsa_demo():
    tab1, tab2 = st.tabs(["Modular arithmetic", "Toy RSA encryption"])

    with tab1:
        _modular_lab()
    with tab2:
        _toy_rsa()


def _modular_lab():
    st.markdown("**Modular arithmetic** underpins public-key cryptography.")
    a = st.number_input("a", value=17, key="mod_a")
    b = st.number_input("b", value=23, key="mod_b")
    m = st.number_input("modulus n", value=12, min_value=2, key="mod_m")
    st.write(f"(a + b) mod n = **{(a + b) % m}**")
    st.write(f"(a × b) mod n = **{(a * b) % m}**")
    if math.gcd(int(a), int(m)) == 1:
        st.write(f"Modular inverse of a mod n: **{pow(int(a), -1, int(m))}**")
    else:
        st.warning("a and n must be coprime for an inverse to exist.")


def _toy_rsa():
    st.markdown("**RSA intuition** — primes p,q; modulus n=pq; encrypt with public exponent e.")
    p = st.selectbox("Prime p", [11, 13, 17, 19, 23], index=1, key="rsa_p")
    q = st.selectbox("Prime q", [29, 31, 37, 41], index=0, key="rsa_q")
    if not (_is_prime(p) and _is_prime(q)):
        st.error("Select primes.")
        return
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537 if phi > 65537 and math.gcd(65537, phi) == 1 else 3
    while math.gcd(e, phi) != 1 and e < phi:
        e += 2
    d = pow(e, -1, phi)
    msg = st.slider("Numeric message (coprime to n)", 2, min(n - 1, 200), 42, key="rsa_msg")
    cipher = pow(msg, e, n)
    plain = pow(cipher, d, n)

    c1, c2, c3 = st.columns(3)
    c1.metric("Modulus n", n)
    c2.metric("Ciphertext", cipher)
    c3.metric("Decrypted", plain)
    st.caption("Real RSA uses 2048+ bit primes; security rests on factoring difficulty.")
