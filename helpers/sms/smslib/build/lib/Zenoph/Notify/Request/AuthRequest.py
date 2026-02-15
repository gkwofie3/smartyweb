from Zenoph.Notify.Request.NotifyRequest import NotifyRequest
from Zenoph.Notify.Response.APIResponse import APIResponse
from Zenoph.Notify.Response.AuthResponse import AuthResponse
from Zenoph.Notify.Store.AuthProfile import AuthProfile
from Zenoph.Notify.Enums.AuthModel import AuthModel

class AuthRequest(NotifyRequest):
    def __init__(self):
        super().__init__()

        # settings
        self._loadAPS = True

    def authenticate(self) ->AuthProfile:
        return self.submit().getAuthProfile()

    def submit(self) ->APIResponse:
        self._setRequestResource("auth")

        # initialise request
        self._initHttpRequest()

        apiResp = super().submit()
        ap = self.__initAuthProfile()

        return AuthResponse.create([apiResp, ap])

    def __initAuthProfile(self) ->AuthProfile:
        ap: AuthProfile = None

        if self._loadAPS:
            ap = AuthProfile()
            ap.setAuthModel(self._authModel)

            if self._authModel == AuthModel.PORTAL_PASS:
                ap.setAuthLogin(self._authLogin)
                ap.setAuthPassword(self._authPsswd)
            elif self._authModel == AuthModel.API_KEY:
                ap.setAuthApiKey(self._authApiKey)

        return ap
