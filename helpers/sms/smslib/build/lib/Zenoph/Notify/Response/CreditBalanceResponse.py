from Zenoph.Notify.Response.APIResponse import APIResponse

from xml.dom import pulldom
from xml.etree import ElementTree

class CreditBalanceResponse(APIResponse):
    CURRENCY_CREDIT_MODEL = 'currency'

    def __init__(self):
        self.__balance: float = 0
        self.__currencyName: str = None
        self.__currencyCode: str = None
        self.__isCurrencyModel: bool = False

    @staticmethod
    def create(apiResp: APIResponse):
        resp = CreditBalanceResponse()
        resp._httpStatusCode = apiResp.getHttpStatusCode()
        resp._handshake = apiResp.getRequestHandshake()

        # extract the balance information
        balanceInfo: dict = CreditBalanceResponse.__extractBalanceInfo(apiResp.getDataFragment())

        # set the balance information
        resp.__balance = balanceInfo['balance'];
        resp.__currencyName = balanceInfo['currencyName']
        resp.__currencyCode = balanceInfo['currencyCode'];
        resp.__isCurrencyModel = balanceInfo['isCurrencyModel']

        # return the balance response object
        return resp

    @staticmethod
    def __extractBalanceInfo(dataFragment: str) ->dict:
        tree: ElementTree.Element = ElementTree.fromstring(dataFragment)
        balanceInfo: dict = {}
        balance = tree.find('balance').text
        isCurrencyCreditModel = True if tree.find('model').text == CreditBalanceResponse.CURRENCY_CREDIT_MODEL else False
        
        balanceInfo['balance'] = float(balance) if isCurrencyCreditModel else int(balance)
        balanceInfo['currencyName'] = tree.find('currencyName').text if isCurrencyCreditModel == CreditBalanceResponse.CURRENCY_CREDIT_MODEL else None
        balanceInfo['currencyCode'] = tree.find('currencyCode').text if isCurrencyCreditModel == CreditBalanceResponse.CURRENCY_CREDIT_MODEL else None
        balanceInfo['isCurrencyModel'] = isCurrencyCreditModel

        # return the balance information
        return balanceInfo


    def getBalance(self) ->float:
        return self.__balance

    def getCurrencyName(self) ->str:
        return self.__currencyName

    def getCurrencyCode(self) ->str:
        return self.__currencyCode

    def isCurrencyModel(self) ->bool:
        return self.__isCurrencyModel