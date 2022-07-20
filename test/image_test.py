from ezml import EzMLApp, EzMLCredentials, EzMLStream



app = EzMLApp("app_id", credentials=EzMLCredentials("username", "password"))  # Creates EzMLApp instance, with credentials
app.deploy() # deploy app

img = "img_path"

EzMLApp.display_results(app.infer_image(img_src=img), img_src=img, save="saved.png", show=True) # infers on image, saves image locally, and displays results in window

