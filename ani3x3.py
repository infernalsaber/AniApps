
import asyncio
import requests
from collections import Counter
import io
import streamlit as st
from math import ceil

from PIL import Image, ImageDraw, ImageFont
import requests_cache
requests_cache.install_cache("my_cache", expire_after=3600)

from image_utils import ImageText

# imgw = ImageText((800, 600), background=(255, 255, 255, 200))
from colour import find_closest_color

def make3x3(images, annotations, names):
    # timeInit = time.time()
    _3x3 = Image.new("RGB", (900,900), (255,255,255))
    draw = ImageDraw.Draw(_3x3) # Danger code
    # draw.text(shadow_position, annotation, font=font, fill=shadow_color)
        # draw.text((x, y), annotation, , fill=(255, 255, 255))
    font = ImageFont.truetype("arial.ttf", 20)

    for i,img in enumerate(images):
        # j = i+1
        x = (i%3)*300
        # if(i%3 == 0):
        #     x = 0
        # elif(i%3 == 1):
        #     x = 300
        # else: x = 600 

        y = int(i/3)*300
            
        # if(i < 3):
        #     y = 0
        # elif(i < 6):
        #     y = 300
        # else: y = 600
        
        # print("I is: ", i)
        size = width, height = img.size
        sizetuple = (0, 0, width, width) if height > width else (0, 0, height, height)
        # print("Size tuple: ", sizetuple)
        
        # '''
        # TODO 
        # If the image is wider, crop centre-wise. For taller ones, height-wise is fine
        # '''
        img = img.crop((0,(height-width)/2, width, (width+height)/2)).resize((300,300))
        # print(img.size)
        # img.show()
        
        _3x3.paste(img, (x,y))
        # draw.text((x,y+240), "\n".join(textwrap.wrap(names[i], width=30)), font=font, fill=(255, 255, 255))
        
        imgw = ImageText((300, 300), background=(255, 255, 255, 0))

        # try:
        text_w, text_h = imgw.write_text_box((0, 0), names[i], font_filename="arial.ttf",
                font_size=20, box_width=300,color=(255,255,255), place='center')
        print(f"{names[i]} pasted")
        
        box_width, box_height = 300, text_h+35
        box_color = (0, 0, 0, 175)  # (R, G, B, Alpha) with Alpha (0-255) specifying transparency

        # Create a new image with the black rectangle
        box_img = Image.new('RGBA', (box_width, box_height), box_color)


        f_colour=find_closest_color(img)
        print("Colour ", f_colour)
        # Paste the black rectangle onto the original image at a specific position
        _3x3.paste(box_img, (x,y+300-text_h-35), mask=box_img)
        draw.text((x+125, y+275), annotations[i], font=font, fill=tuple(f_colour)) #Danger code
        
        # except Exception as e:
        #     print(e, " Second")    
            # imgw.show()
            # test_image = Image.open("test.png")
        text_image = imgw.get_image()
        # try:
        print("Text height", text_h)
        print("Text width", text_w)
        _3x3.paste(text_image, (x, y+275-text_h-25), mask=text_image)
        # except Exception as e:
        #     print(e, " Third")
        
        # _3x3.show()
    # print("time: ", time.time()-timeInit)
    return _3x3


def id_to_image(ids: int, item_type:str = "MANGA") -> Image:
    query = """
query ($search: Int, $item_type: MediaType) { # Define which variables will be used (id)
Media (id: $search, type: $item_type) { # The sort param was POPULARITY_DESC
    coverImage {
        large
    }
    }
}
"""

    variables = {"search": ids, "type": item_type}

    req =  requests.post(
    "https://graphql.anilist.co",
    json={"query": query, "variables": variables},
    timeout=10,
    ).json()
    a = Image.open(io.BytesIO(requests.get(req['data']['Media']['coverImage']['large']).content))
    # a.show()
    return a

def give_user_scores(user: str, type: str = "MANGA"):
    query = """
query ($search: String, $type: MediaType) { # Define which variables will be used (id)
MediaListCollection (userName: $search, type: $type) { # The sort param was POPULARITY_DESC
    lists {
        entries {
            score (format: POINT_10_DECIMAL)
            media {
                id
                title {
                    romaji
                }
            }
        }
    }
}
}

"""

    variables = {"search": user, "type": type}

    req =  requests.post(
    "https://graphql.anilist.co",
    json={"query": query, "variables": variables},
    timeout=10,
    ).json()
    # print(req)
    scores = []
    for lists in req['data']['MediaListCollection']['lists']:
        for entry in lists['entries']:
            if entry['score'] > 0.1:
                scores.append([entry['media']['id'], entry['media']['title'], entry['score']])
    # print(scores)
    return scores



def grid_maker(
    users, 
    gridtype: str = "MANGA", 
    threshold:int=None,
    annotations: list = None,
    colours: list = None
    ):

    final_scores = []
    for user in users:
        final_scores += give_user_scores(user,gridtype)

    # final_scores




    # Sample list of lists
    data = final_scores

    # Use Counter to count the occurrences of the first entries
    counts = Counter(entry[0] for entry in data)

    # Create a dictionary to store the sum and count for each first entry
    averages = {}

    # Iterate over the data and update the sums and counts in the dictionary
    for entry in data:
        key = entry[0]
        name = entry[1]
        value = entry[2]
        if key not in averages:
            averages[key] = {'sum': value, 'count': 1, 'name': name}
        else:
            averages[key]['sum'] += value
            averages[key]['count'] += 1

    # Create a new list with averaged values and counters
    result = []
    # print(averages)
    for key in averages:
        average_value = averages[key]['sum'] / averages[key]['count']
        result.append([key, averages[key]['name'], average_value, counts[key]])

    # Print the result
    # result



    def sort_list(e):
        return e[2]

    result.sort(key=sort_list)
    # result



    real_final_list = []

    for item in result:
        if item[3]>= threshold:
            real_final_list.append(item)
        
    def final_sorter(e):
        return e[2]

    real_final_list.sort(key=final_sorter, reverse=True)
    # real_final_list

    # print(real_final_list)








    final_images = []

    for item in real_final_list[:9]:
        final_images.append(id_to_image(item[0], gridtype))









    annotations = []
    names = []
    for item in real_final_list[:9]:
        annotations.append(item[2])
        names.append(item[1]['romaji'])



    new = []
    for ratings_dec in annotations:
        # ratings_dec = "{:.2f}".format(ratings_dec)
        new.append("{:.2f}".format(ratings_dec))




    final_images_3x3 = make3x3(final_images, new, names)
    return final_images_3x3




async def main3x3():
    st.title("3x3 Maker")
    threshold = 1
    users = st.text_input('Enter the usernames')
    users = [user.strip() for user in users.split(",")]
    if len(users) > 10:
        st.error("Too many users")
        return
    list_type = st.selectbox('Type',['Anime','Manga', 'Character (COMING SOON)'])
    list_type = list_type.upper()
    c1, c2 = st.columns(2)
    with c1:
        if len(users) > 1:
            threshold = st.slider(
                'Threshold',
                min_value=1, max_value=len(users),
                value=ceil(0.4*len(users))
            )

    with c2:
        if list_type[0] != 'C':
            selection_criteria = st.selectbox('Based on',['Ratings', 'Favourites'])


    with st.expander("Advanced options"):
        c1, c2 = st.columns(2)
        with c1:
            annotate1 = st.checkbox("Add Series' Name", value=True)
        with c2:
            annotate2 = st.checkbox('Add Ratings', value=True)
        c1, c2 = st.columns(2)
        with c1:
            text_color = st.color_picker("Pick Text Colour")
        with c2:
            highlight_color = st.color_picker("Pick Background Colour")


    if st.button("Start Cooking"):

        with st.spinner("Cooking..."):
            image = grid_maker(
                users, list_type, threshold, [annotate1, annotate2], [text_color, highlight_color]
            )
            st.header("Your 3x3 is here:")
    
        st.image(image, caption='Your collaborative 3x3')

if __name__ == "__main__":
    asyncio.run(main3x3())