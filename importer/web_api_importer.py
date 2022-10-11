# export PYTHONPATH=$PYTHONPATH:/Users/willidragon/Desktop/chemcloud/chemicloud-backend
# export DJANGO_SETTINGS_MODULE=chemicloud-backend.settings

from unittest import skip
import django

django.setup()
from chemical.models import Place, Paction, Chemical, Transaction
from loguru import logger

import requests
import json

url = "https://flora2.epa.gov.tw/ToxicAPI/OChain/GetPermits"
myobj = {"Name": "AAEAE5C6-7F80-4D0C-B025-54361F724B22"}

req = requests.post(url, json=myobj)
req_json = req.json()
api_data = req_json["data"]

# for testing
# x={'Type': 1, 'C_No': 'H51A3887', 'Place_No': 'H51A3887', 'Toxic_No': '11901', 'Per_No': '新北市毒核字第000461號', 'Q11': 95.0, 'Q12': 100.0, 'Act': '使用貯存', 'DateAD': '2020-11-11T00:00:00', 'DateDel': '2020-12-18T00:00:00'}
# y = json.dumps(x)
# api_data = json.loads(y)


# def create_transaction(data):
#     C_No_exist = Place.objects.filter(place_no=data['C_No'])
#     placeNo_exist = Place.objects.filter(place_no=data['Place_No'])
#     chem_exist = Chemical.objects.filter(certificate_no=data['Toxic_No'])
#     paction_exist =Paction.objects.filter(paction_no=data['Per_No'])
#     if(C_No_exist and placeNo_exist and chem_exist and paction_exist):
#         #transaction volume is set to 0 b/c api does not contain info regarding volume traded
#         newTranscation = Transaction(transaction_date=data['DateAD'].split('T', 1)[0], transaction_behavior=data['Act'], transaction_volume=0,
#                                  certificate_no_id=data['Toxic_No'], place_no_id=data['C_No'], target_place_no_id=data['Place_No'])
#         newTranscation.save()
#         logger.info(f"creating transaction #{newTranscation.transaction_id}")
#     else:
#         logger.info("some param not found, skip creating transaction")


def update_paction(data):
    paction_exist = Paction.objects.filter(paction_no=data["Per_No"])
    if paction_exist:
        paction_data = paction_exist.first()
        paction_data.paction_issue_date = data["DateAD"].split("T", 1)[0]
        paction_data.paction_valid_date = data["DateDel"].split("T", 1)[0]
        paction_data.paction_type = data["Act"]
        paction_data.save()
        logger.info(f"updating paction #{data['Per_No']}")
    else:
        C_No_exist = Place.objects.filter(place_no=data["C_No"])
        placeNo_exist = Place.objects.filter(place_no=data["Place_No"])
        if C_No_exist and placeNo_exist:
            newPaction = Paction(
                paction_no=data["Per_No"],
                paction_type=data["Act"],
                paction_issue_date=data["DateAD"].split("T", 1)[0],
                paction_valid_date=data["DateDel"].split("T", 1)[0],
                place_no_id=data["C_No"],
            )
            newPaction.save()
            logger.info(f"creating paction #{data['Per_No']}")


for item in api_data:
    update_paction(item)
    # create_transaction(item)
