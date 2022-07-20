from ezml import EzMLApp, EzMLCredentials, EzMLStream


app = EzMLApp("app_id", credentials=EzMLCredentials("username", "password"))  # Creates EzMLApp instance, with credentials
app.deploy() # deploy app

vid_src = "vid_src"

app.infer_video(vid_src, save="save_name.mp4") # INFERS ON VIDEO AND SAVES TO GIVEN PATH