#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3824979
# ----------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""Methods supporting the Global Navigation Satellite System platform."""


def acknowledgements(name):
    """Provide the acknowledgements for different GNSS instruments.

    Parameters
    ----------
    name : str
        Instrument name

    Returns
    -------
    ackn : str
        Acknowledgement information to provide in studies using this data

    """
    ackn = {'tec': ''.join(["GPS TEC data products and access through the ",
                            "Madrigal distributed data system are provided to ",
                            "the community by the Massachusetts Institute of ",
                            "Technology under support from U.S. National ",
                            "Science Foundation grant AGS-1242204. Data for ",
                            "the TEC processing is provided by the following ",
                            "organizations: UNAVCO, Scripps Orbit and ",
                            "Permanent Array Center, Institut Geographique ",
                            "National, France, International GNSS Service, The",
                            " Crustal Dynamics Data Information System ",
                            "(CDDIS), National Geodetic Survey, Instituto ",
                            "Brasileiro de Geografiae Estatística, RAMSAC ",
                            "CORS of Instituto Geográfico Nacional del la ",
                            "República Agentina, Arecibo Observatory, ",
                            "Low-Latitude Ionospheric Sensor Network (LISN), ",
                            "Topcon Positioning Systems, Inc., Canadian High ",
                            "Arctic Ionospheric Network, Institute of Geology",
                            " and Geophysics, Chinese Academy of Sciences, ",
                            "China Meterorology Administration, Centro di ",
                            "Niveau des Eaux Littorales Ricerche Sismogiche, ",
                            "Système d’Observation du  (SONEL), RENAG : ",
                            "REseau NAtional GPS permanent, and GeoNet—the ",
                            "official source of geological hazard information ",
                            "for New Zealand."])}

    return ackn[name]


def references(name):
    """Provide suggested references for the specified data set.

    Parameters
    ----------
    name : str
        Instrument name

    Returns
    -------
    refs : str
        Suggested Instrument reference(s)

    """
    refs = {'tec': "Rideout and Coster (2006) doi:10.1007/s10291-006-0029-5"}

    return refs[name]
