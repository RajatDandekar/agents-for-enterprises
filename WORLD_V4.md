# The v4 world: Northbridge Cycles (replaces Rasoi Steel Works)

Rajat, 2026-10-30: "Rasoi, Kavita etc. sound very Indian, we should take global names and examples. The example of cookers is not good." He chose the e-bike maker. Every lecture moves to this world as it is rebuilt: L1 now, then L2 by Sun 1 Nov, and the rest in order. Until a lecture is rebuilt, its notebook installs the frozen `v3.1` tag.

The mechanical rename is `tools/world_v4.py` (names, codes, places, tax, currency). Battery numbers and narrative text are edited by hand.

## The company
- **Northbridge Cycles** makes electric bikes, with a plant in Manchester (`NBC-MAN-01`) and a unit in Leeds (`NBC-LDS-01`). It sells through bike shops across the UK and Europe, about 18,000 e-bikes a month.
- **The legacy ERP:** **Ledgerline ERP 7.2**, bought in 1998. The Python package is `ledgerline` (pip `ledgerline-erp`), with `LedgerlineError` and env vars `LEDGER_*` (for example `LEDGER_LLM_MODE`).
- **The assistant:** **Ask Northbridge**. The live app is **the Northbridge Experience** (Modal app `northbridge-experience`).
- **Money:** £ (GBP), VAT 20%. Tax codes are `VAT20-UK` (UK supplier) and `VAT20-RC` (reverse charge, overseas supplier), plus `VAT5-*`. ERR-PO-0412 now reads "TAX CODE DOES NOT MATCH SUPPLIER COUNTRY". The sandbox clock is Mon 26 Oct 2026, 09:00 GMT.

## People (pronouns as given)
| Code | Name | Role |
|---|---|---|
| ECLARKE | Emma Clarke (she) | purchase executive. Limit £250,000 gross incl. VAT |
| DOKAFOR | Daniel Okafor (he) | purchase manager. Limit £1,000,000 |
| LMORENO | Luis Moreno (he) | senior buyer. Knows the rules that never made it into the ERP |
| HWEBER | Henrik Weber (he) | plant head. Wrote the letter to the engineer |
| ATANAKA | Aiko Tanaka (she) | stores. Records the goods receipt |
| SVC_AGENT | integration service account | the all-powerful account "for the bot" |

## The order (replaces 20,000 gaskets)
- Emma needs **2,000 battery packs** (`BAT-500`, "Battery pack, 36 V 500 Wh") for the **spring launch run** (cost centre `PRD-07`).
- **Supplier:** **Voltway Cells**, Eindhoven, NL (`VC-EIN-0042`), at the contract rate **£119.00**. There is an old blocked code, `VC-EIN-0009`.
- **Value:** basic £238,000; VAT 20% £47,600; gross **£285,600**. That is above Emma's limit, so Daniel must approve. Request estimate: 2,000 × £114.00 × 1.20 = £273,600.
- **Stock:** 5,400 in Manchester plus 1,200 in Leeds. About 600 are used a day, so 9 days of cover. Reorder level 3,000.
- **Traps carried over:**
  - **Which Voltway?** Voltway Paints & Coatings, Rotterdam (`VPC-ROT-0107`), is a different supplier.
  - **Wrong tax code:** the default is `VAT20-UK`, but Voltway is overseas, so the order needs `VAT20-RC` (ERR-PO-0412).
  - **Closed cost centre:** `PRD-05`, the city e-bike line, closed on 15 Oct.
  - **Saved is not done:** "SAVED" while the order sits in Draft.
  - **Delivery:** Aiko receives 1,200 packs (delivery note DN-4471), then 800.

## The certification rule (§6.2, replaces food-grade)
Lithium-cell parts need a supplier with a valid **UN 38.3** certificate: battery packs `BAT-*`, hub motor `MTR-HUB-250` and charger `CHG-4A-01`. The `item.cell_safety` flag marks these parts.
- **Certified:** Voltway Cells, Castlefield Chargers (Salford), Albion Motors (Birmingham).
- **Expired** (30 Sep 2026): **Nordic Cell Co.**, Gdańsk, which is cheaper at £111.00.
- **Not in the master:** **Brightcell Energy**, Lyon, the new cheaper supplier quoting £104.00.

## Other suppliers and items
- **Suppliers:**
  - Pennine Brakes, Manchester (`PB-MAN-0017`): bells and brake pads.
  - Irwell Packaging, Manchester (`IP-MAN-0055`): bike cartons.
- **Items:**
  - Battery mounts `MNT-FRM-01` and `MNT-RCK-02`, from Voltway.
  - Bell `BEL-STD-01`.
  - Brake pads `BRK-PAD-01`.
  - Carton `BOX-BIKE-01`.

## Rules for every builder
- Never use Indian names, places, festivals, GST, ₹, lakh or crore, or the old client's name. Run `python3 tools/world_v4.py --check <paths>` before you finish.
- Recorded replies (cassettes) are keyed by a hash of the request. A renamed run is a new run: re-record it, and never copy numbers from the Rasoi runs.
