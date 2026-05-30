"""Astronomy simulations — orbits and exoplanet transit detection."""

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st


def exoplanet_transit():
    st.markdown("**Transit photometry** — detect planetary radius from stellar dimming.")
    star_radius = st.slider("Stellar radius (solar units)", 0.5, 2.0, 1.0, key="tr_rstar")
    planet_radius = st.slider("Planet radius (Earth radii)", 0.5, 15.0, 3.0, key="tr_rpl")
    noise_ppm = st.slider("Photometry noise (ppm)", 50, 2000, 400, key="tr_noise")
    depth_ppm = (planet_radius / 109.2) ** 2 * 1e6 * (star_radius ** -2)

    t = np.linspace(-0.2, 0.2, 400)
    flux = np.ones_like(t)
    transit_mask = np.abs(t) < 0.05
    flux[transit_mask] = 1 - depth_ppm / 1e6
    flux += np.random.normal(0, noise_ppm / 1e6, size=t.shape)

    fig, ax = plt.subplots()
    ax.plot(t, flux, linewidth=1)
    ax.set_xlabel("Time (relative, orbital phases)")
    ax.set_ylabel("Relative flux")
    ax.set_title("Simulated Exoplanet Transit Light Curve")
    ax.grid(True)
    st.pyplot(fig)
    plt.close(fig)

    st.metric("Transit depth (ppm)", f"{depth_ppm:.0f}")
    st.caption("Kepler/TESS pipelines fit this dip to estimate planet size and orbital period.")


def orbital_mechanics():
    eccentricity = st.slider("Orbital eccentricity", 0.0, 0.85, 0.35, key="orb_e")
    steps = st.slider("Time steps", 100, 1200, 500, key="orb_n")

    theta = np.linspace(0, 4 * np.pi, steps)
    r = 1 / (1 + eccentricity * np.cos(theta))
    x = r * np.cos(theta)
    y = r * np.sin(theta)

    fig, ax = plt.subplots()
    ax.plot(x, y, color="#0ea5e9")
    ax.scatter([0], [0], color="gold", s=140, zorder=5, label="Central body")
    ax.set_aspect("equal")
    ax.set_title("Keplerian Orbit — inverse-square dynamics")
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)
    plt.close(fig)
