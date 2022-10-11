# Remember to set DJANGO_SETTINGS_MODULE
# like: export DJANGO_SETTINGS_MODULE=chemicloud-backend.settings
# also: export PYTHONPATH=$PYTHONPATH:/Users/willidragon/Desktop/chemcloud/chemicloud-backend
# import sys
# sys.path.append("/Users/willidragon/Desktop/chemcloud/chemicloud-backend")
# filepath- /Users/willidragon/Downloads/1928_short.json

import django

django.setup()
import argparse
from json_fixer import fix_and_read_json
from chemical.models import Place, Paction, Chemical, Transaction
from django.apps import apps
import json
from loguru import logger


parser = argparse.ArgumentParser()
parser.add_argument("--path", help="filepath to open")
args = parser.parse_args()
data = fix_and_read_json(args.path)


def check_CTNO_exist(temp_place_no):
    CTNO_exist = Place.objects.filter(place_no=temp_place_no)
    if CTNO_exist:
        logger.info(f"CTNO already exist={temp_place_no}")

    else:
        logger.info(f"CTNO doesn't exist={temp_place_no}, creating new place entry")
        newPlace = Place(place_no=temp_place_no, place_name="", company_name="")
        newPlace.save()


def check_TgtCTNO_exist(temp_place_no, temp_company_name, temp_addr):
    TgtCTNO_exist = Place.objects.filter(place_no=temp_place_no)
    if TgtCTNO_exist:
        logger.info(f"TgtCTNO already exist={temp_place_no}")

    else:
        logger.info(f"TgtCTNO doesn't exist={temp_place_no}, creating new place entry")
        newPlace = newPlace = Place(
            place_no=temp_place_no, place_name=temp_addr, company_name=temp_company_name
        )
        newPlace.save()


def check_ChemCN_CTNOconc_exist(temp_CN, temp_place_no, tempconcentration, data):
    chain_exist = (
        Chemical.objects.filter(chemical_name=temp_CN)
        .filter(place_no_id=temp_place_no)
        .filter(chemical_concentration=tempconcentration)
    )
    if chain_exist:
        logger.info(
            f"ChemCN_CTNOconc pair exist={temp_CN},{temp_place_no},{tempconcentration}"
        )

    else:
        logger.info(
            f"ChemCN_CTNOconc pair doesn't exist={temp_CN},{temp_place_no},{tempconcentration}, creating new Chemical entry"
        )
        Chem_id = data["ToxConNo"]

        chemCat = ""
        cat_map = {1: "毒", 2: "關", 3: "其他"}
        chemCat = cat_map.get(data["ChemCat"], "")

        newChemical = Chemical(
            chemical_name=temp_CN,
            place_no_id=temp_place_no,
            chemical_concentration=tempconcentration,
            certificate_no=Chem_id,
            material_type=chemCat,
            holdings=0,
        )
        newChemical.save()


def check_paction_exist(temp_paction_name, temp_paction_action, temp_place_no):
    paction_exist = Paction.objects.filter(paction_no=temp_paction_name)
    if paction_exist:
        logger.info(f"paction exist:{temp_paction_name}")

    else:
        logger.info(
            f"paction doesn't exist:{temp_paction_name}, creating new Paction entry"
        )
        _paction_action_type = ""
        paction_map = {
            1: "製造",
            10: "使用",
            2: "輸入",
            3: "輸出",
            4: "買入",
            5: "賣出",
            6: "撥入",
            7: "撥出",
            8: "殘氣退回",
            9: "殘氣收回",
        }

        _paction_action_type = paction_map.get(temp_paction_action, "")

        newPaction = Paction(
            paction_no=temp_paction_name,
            paction_type=_paction_action_type,
            paction_issue_date="2022-02-02",
            paction_valid_date="2022-02-02",
            place_no_id=temp_place_no,
        )
        newPaction.save()


def create_transaction(
    temp_transaction_date,
    temp_paction_action,
    temp_action_qty,
    temp_place_id,
    temp_tgt_place_id,
    chem_id,
):

    _paction_action_type = ""
    paction_map = {
        1: "製造",
        10: "使用",
        2: "輸入",
        3: "輸出",
        4: "買入",
        5: "賣出",
        6: "撥入",
        7: "撥出",
        8: "殘氣退回",
        9: "殘氣收回",
    }
    _paction_action_type = paction_map.get(temp_paction_action, "")

    _queryset = (
        Transaction.objects.filter(transaction_date=temp_transaction_date)
        .filter(transaction_behavior=_paction_action_type)
        .filter(transaction_volume=temp_action_qty)
        .filter(certificate_no_id=chem_id)
        .filter(place_no_id=temp_place_id)
        .filter(target_place_no_id=temp_tgt_place_id)
    )

    if not _queryset:
        newTranscation = Transaction(
            transaction_date=temp_transaction_date,
            transaction_behavior=_paction_action_type,
            transaction_volume=temp_action_qty,
            certificate_no_id=chem_id,
            place_no_id=temp_place_id,
            target_place_no_id=temp_tgt_place_id,
        )
        newTranscation.save()
        logger.info(f"creating transaction #{newTranscation.transaction_id}")
    else:
        logger.info("transaction already exists")


def allocate_chemical_paction(
    temp_CN,
    temp_place_no,
    tempconcentration,
    temp_paction_action,
    permit_no,
    target_permit_no,
):
    _queryset = (
        Chemical.objects.filter(chemical_name=temp_CN)
        .filter(place_no_id=temp_place_no)
        .filter(chemical_concentration=tempconcentration)
    )
    paction_exist = Paction.objects.filter(paction_no=permit_no).first()
    target_paction_exist = Paction.objects.filter(paction_no=target_permit_no).first()
    if _queryset and paction_exist and target_paction_exist:
        _Chemical = _queryset.first()
        if temp_paction_action == 1:
            # produce
            _Chemical.paction_no_produce_id = paction_exist.paction_blockchain_id
            _Chemical.save()
        elif temp_paction_action == 4:
            # import
            _Chemical.paction_no_import_id = target_paction_exist.paction_blockchain_id
            _Chemical.save()
        elif temp_paction_action == 5:
            # export
            _Chemical.paction_no_export_id = target_paction_exist.paction_blockchain_id
            _Chemical.save()


for item in data["ChemOps"][0]:

    data = item

    place_no = data["CTNO"]
    tgt_place_no = data["TgtCTNO"]
    tgt_company_name = data["TgtComFacN"]
    tgt_company_place = data["TgtForAddr"]
    Chem_CN = data["ChemCN"]
    conc = data["CONC"]
    permit_no = data["PermitNo"]
    target_permit = data["TgtPermitNo"]
    paction_action = data["TCAction"]
    target_no = data["TgtPermitNo"]
    transaction_date = data["OpDate"]
    transaction_qty = data["Qty"]
    chem_id = data["ToxConNo"]

    # change chem name
    temp_string = data["ChemCN"]
    temp_string = temp_string.split("[", 1)[0]
    temp_string = temp_string.split("（", 1)[0]
    temp_string = temp_string.replace("*", "")
    Chem_CN = temp_string

    check_TgtCTNO_exist(tgt_place_no, tgt_company_name, tgt_company_place)
    check_CTNO_exist(place_no)
    check_ChemCN_CTNOconc_exist(Chem_CN, place_no, conc, data)
    check_paction_exist(permit_no, paction_action, place_no)
    # check_paction_exist(target_no, "target", tgt_place_no)
    create_transaction(
        transaction_date,
        paction_action,
        transaction_qty,
        place_no,
        tgt_place_no,
        chem_id,
    )
    allocate_chemical_paction(
        Chem_CN, place_no, conc, paction_action, permit_no, target_permit
    )
