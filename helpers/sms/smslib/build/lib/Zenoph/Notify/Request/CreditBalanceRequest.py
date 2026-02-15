
from Zenoph.Notify.Request.NotifyRequest import NotifyRequest
from Zenoph.Notify.Response.CreditBalanceResponse import CreditBalanceResponse

class CreditBalanceRequest(NotifyRequest):
    def __init__(self, ap = None):
        super().__init__(ap)

    def submit(self):
        # set the request resource
        self._setRequestResource('account/balance')

        # initialise HTTP request and submit
        self._initHttpRequest()

        # submit for response
        resp = super().submit()

        # create and return the balance response
        return CreditBalanceResponse.create(resp)
