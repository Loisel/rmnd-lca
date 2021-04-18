import wurst
import wurst.searching as ws
from .geomap import Geomap
from .activity_maps import InventorySet
import numpy as np

def apply_gains_ef_improvements(year, db, model, iam_data):
    mapping = InventorySet(db)
    emissions_map = mapping.get_remind_to_ecoinvent_emissions()
    geo = Geomap(model=model)
    
    def update_GAINS_pollutant_emissions(ds, gains_sector):

        gains_data = iam_data.gains_data.sel(sector=gains_sector)
        # Update biosphere exchanges according to GAINS emission values
        for exc in ws.biosphere(
                ds, ws.either(*[ws.contains("name", x) for x in emissions_map])
            ):
            remind_emission_label = emissions_map[exc["name"]]

            loc = geo.ecoinvent_to_iam_location(ds["location"])

            correction_factor = (gains_data.loc[
                                     dict(
                                         region="CHA" if loc == "World" else loc,
                                         pollutant=remind_emission_label
                                     )
                                 ].interp(year=year)
                                 /
                                 gains_data.loc[
                                     dict(
                                         region="CHA" if loc == "World" else loc,
                                         pollutant=remind_emission_label,
                                         year=2020
                                     )
                                 ]).values.item(0)

            if correction_factor != 0 and ~np.isnan(correction_factor):
                if exc["amount"] == 0:
                    wurst.rescale_exchange(
                        exc, correction_factor / 1, remove_uncertainty=True
                    )
                else:
                    wurst.rescale_exchange(exc, correction_factor)

                exc["comment"] = "This exchange has been modified based on GAINS projections for the steel sector by `premise`."
        return ds

    # coking
    for ds in ws.get_many(
            db,
            ws.equals("name", "coking")):
        update_GAINS_pollutant_emissions(ds, "End_Use_Industry_Coal")
    # iron sintering
    for ds in ws.get_many(
            db,
            ws.equals("name", "iron sinter production")):
        update_GAINS_pollutant_emissions(ds, "STEEL")
    # industrial heat
    for ds in ws.get_many(
            db,
            ws.contains("name", "heat production, at hard coal industrial furnace")):
        update_GAINS_pollutant_emissions(ds, "End_Use_Industry_Coal")
    # generators for mining
    for ds in ws.get_many(
            db,
            ws.contains("name", "diesel, burned in diesel-electric generating set"),
            ws.exclude(ws.contains("name", "market for diesel"))):
        update_GAINS_pollutant_emissions(ds, "Power_Gen_HLF")
    # aluminium
    for ds in ws.get_many(
            db,
            ws.contains("name", "aluminium production, primary")):
        update_GAINS_pollutant_emissions(ds, "CUSM")

