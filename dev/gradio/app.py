import gradio as gr

#Custom theme: RED as in our prototype
theme = gr.themes.Base(
    primary_hue="red",
).set(
    button_primary_background_fill='*primary_500',
    button_primary_text_color='*neutral_50'
)
selected_mood = 0
#here we could bind in the link to the playlists in the DB
playlist = ["images/Alan Walker - Dreamer [NCS Release].mp3", "images/Diamond Eyes - Stay [NCS Release].mp3" ]
title = ["Alan Walker - Dreamer", "Diamond Eyes - Stay"]

#testing method, might delete later
def update_message(request: gr.Request):
    return f"{request.username}"

#behavior when clicking on a button: change to player tab
def change_tab():
    selected_mood = 1
    return gr.Tabs(selected=1)
    #home.load(change_tab, None, gr.Tabs(selected=1))




#our site is one big block
with gr.Blocks(theme=theme) as home:
    #the following line is needed to let the browser access the data:
    gr.set_static_paths(paths=["images/"])
    #we're using 2 tabs, one for the homepage and one for settings
    with gr.Tabs() as tabs:
        with gr.TabItem("Home", id=0):
            #we use rows to organize our content
            with gr.Row():
                html1 = gr.HTML("""
                <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                    <div style="display: flex; align-items: center;">
                        <img src="/file=images/play.png" style="height: 50px; margin-right: 10px;">
                        <h2 style="margin: 0;"><b>PlayNext</b></h2>
                    </div>
                <h3 style="margin: 0; text-align: right;">Settings</h3>
                </div>
                """)
            with gr.Row():
                html2 = gr.HTML("""
                <div style="display: flex; align-items: center;">
                <h1><b>How do you feel today?</b></h1>
                </div>
                """)
            with gr.Row():
                button1 = gr.Button(value="Happy", variant="primary")
                button1.click(change_tab, None, tabs) #doesn't select anything yet, just changes tab
                button2 = gr.Button(value="Sad", variant="primary")
                button2.click(change_tab, None, tabs)
                button3 = gr.Button(value="Energized", variant="primary")
                button3.click(change_tab, None, tabs)
                button4 = gr.Button(value="Tired", variant="primary")
                button4.click(change_tab, None, tabs)
                button5 = gr.Button(value="more...", variant="primary")
                button5.click(change_tab, None, tabs)

            with gr.Row():
                html3 = gr.HTML("""
                <div style="display: flex; align-items: center;">
                <h1><b>Music for your mood:</b></h1>
                </div>
                """)
    
    
            with gr.Row():
                html4 = gr.HTML("""
                    <div style="display: flex; align-items: center;">
                    <img src="/file=images/pexels-andre-furtado-1263986.jpg" style="height: 120px; margin-right: 10px;">
                    </div>
                    """)
                html5 = gr.HTML("""
                    <div style="display: flex; align-items: center;">
                    <img src="/file=images/pexels-renato-1264438.jpg" style="height: 120px; margin-right: 10px;">
                    </div>
                    """)
                html6 = gr.HTML("""
                    <div style="display: flex; align-items: center;">
                    <img src="/file=images/pexels-pixabay.jpg" style="height: 120px; margin-right: 10px;">
                    </div>
                    """)
                html7 = gr.HTML("""
                    <div style="display: flex; align-items: center;">
                    <img src="/file=images/pexels-acharaporn-kamornboonyarush-1028741.jpg" style="height: 120px; margin-right: 10px;">
                    </div>
                    """)

            with gr.Row():
                html4 = gr.HTML("""
                <div style="display: flex; align-items: center;">
                <h1><b>Your favorite songs:</b></h1>
                </div>
                """)

            with gr.Row():
                m = gr.Markdown()

            with gr.Row():
                logout_button = gr.Button("Logout", link="/logout")

            #home.load(update_message, None, m)
        with gr.TabItem("Player", id=1):
            with gr.Blocks(theme=theme) as player:
                with gr.Row():
                    gr.Audio(value=playlist[selected_mood])

    


home.launch()  
