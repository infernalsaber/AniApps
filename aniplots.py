"""The extension which fetches the AL data for the plot function"""
import datetime
from operator import itemgetter

import requests
import requests_cache
import asyncio
requests_cache.install_cache("my_cache", expire_after=3600)

import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

import streamlit as st

async def search_it(search_query: str) -> dict | int:
    # """Search for the anime"""
    # Here we define our query as a multi-line string
    query = """
query ($id: Int, $search: String) { 
    Media (id: $id, search: $search, type: ANIME, sort: POPULARITY_DESC) { 
        id
        title {
            english
            romaji
        }
        averageScore
        startDate {
            year
            month
            day
        }
        endDate {
            year
            month
            day
        }
        coverImage {
            large
        }
        status

    }
}

    """

    # Make the HTTP Api request
    response = requests.post(
        "https://graphql.anilist.co",
        json={"query": query, "variables": {"search": search_query}},
        timeout=10,
    )
    if response.status_code == 200:
        print("Successfull connection")
        data = response.json()["data"]["Media"]
        al_id = data["id"]
        name = data["title"]["english"] or data["title"]["romaji"]
        lower_limit = datetime.datetime(
            data["startDate"]["year"],
            data["startDate"]["month"],
            data["startDate"]["day"],
            0,
            0,
        )

        if datetime.datetime.now() < lower_limit:
            print("Unaired stuff sir")
        lower_limit = lower_limit - datetime.timedelta(days=7)
        if data["endDate"]["year"]:
            upper_limit = datetime.datetime(
                data["endDate"]["year"],
                data["endDate"]["month"],
                data["endDate"]["day"],
                0,
                0,
            ) + datetime.timedelta(days=7)
        else:
            upper_limit = datetime.datetime.now()

    else:
        print(response.json()["errors"])
        return response.status_code

    # """Fetching the trend values """
    req = requests.Session()
    # id = input("Enter id. ")
    trend_score = []
    flag = True
    counter = 1

    while flag:
        query = """
        query ($id: Int, $page: Int, $perpage: Int, $date_greater: Int, $date_lesser: Int) {
        Page (page: $page, perPage: $perpage) { 
            pageInfo {
                total
                hasNextPage
            }
            mediaTrends (mediaId: $id, date_greater: $date_greater, date_lesser: $date_lesser) {
            mediaId
            date
            trending
            averageScore
            episode
            }
            }
        }
        """

        variables = {
            "id": al_id,
            "page": counter,
            "perpage": 50,
            "date_greater": lower_limit.timestamp(),
            "date_lesser": int(upper_limit.timestamp()),
        }

        response = req.post(
            "https://graphql.anilist.co", json={"query": query, "variables": variables}
        )

        if response.status_code == 200:
            # print(response.json())
            if not response.json()["data"]["Page"]["pageInfo"]["hasNextPage"]:
                flag = False
            else:
                counter = counter + 1

            for item in response.json()["data"]["Page"]["mediaTrends"]:
                trend_score.append(item)
        else:
            # print("ERROR")
            print(response.json()["errors"])
            return response.status_code

    # Parsing the values

    dates = []
    trends = []
    scores = []

    episode_entries = []
    trends2 = []
    dates2 = []

    for value in trend_score:
        if value["episode"]:
            episode_entries.append(value)

    for value in sorted(episode_entries, key=itemgetter("date")):
        trends2.append(value["trending"])
        dates2.append(datetime.datetime.fromtimestamp(value["date"]))

    for value in sorted(trend_score, key=itemgetter("date")):
        dates.append(datetime.datetime.fromtimestamp(value["date"]))
        trends.append(value["trending"])
        if value["averageScore"]:
            scores.append(value["averageScore"])

    # Sending the data back

    return {
        "name": name,
        "data": [dates, trends, dates2, trends2, dates[-len(scores) :], scores],
    }


async def compare_trends(query: str) -> None:
    # """Compare the popularity and ratings of two different anime
    # Args:
    #     ctx (lb.Context): The event context (irrelevant to the user)
    #     query (str): The name of the two anime (seperated by "vs")
    # """

    # print(os.listdir("./pictures/"))
    # print("\n\n\n")
    # if f"{query}.png" in os.listdir("./pictures/"):
    #     # await ctx.respond("Found")
    #     await ctx.respond(
    #         embed=hk.Embed(
    #             title=f"Popularity Chart: {query}", color=0x7DF9FF
    #         ).set_image(hk.File(f"pictures/{query.upper()}.png"))
    #         # , attachments = None
    #     )

        # return
    series = query.split("vs")
    # if not len(series) in [1, 2]:
    #     await ctx.respond("The command only works for one or two series.")
    #     return

    # async with ctx.bot.rest.trigger_typing(ctx.event.channel_id):
    if len(series) == 1:
        data = await search_it(series[0])

        # if isinstance(data, int):
        #     await ctx.respond(f"An error occurred, `code: {data}` ")
        #     return
        # print(type(data))

        pio.renderers.default = "notebook"
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(
                x=data["data"][0],
                y=data["data"][1],
                mode="lines",
                name="Trends",
                line={"color": "MediumTurquoise", "width": 2.5},
            )
        )
        fig.add_trace(
            go.Scatter(
                x=data["data"][2],
                y=data["data"][3],
                mode="markers",
                name="Episodes",
                line={"color": "MediumTurquoise", "width": 2.5},
            )
        )
        fig.add_trace(
            go.Scatter(
                x=data["data"][4],
                y=data["data"][5],
                line={"color": "DeepPink"},
                name="Scores",
                mode="lines",
                line_shape="spline",
            ),
            secondary_y=True,
        )
        fig.update_layout(
            # title=f'Series Trends: {data["name"]}',
            xaxis_title="Dates",
            yaxis_title="Trend Value",
            template="plotly_dark",
        )
        """TEST"""
        st.header(f"Popularity Trends: {data['name']}")
    else:
        data = await search_it(series[0])
        # from pprint import pprint
        data2 = await search_it(series[1])

        pio.renderers.default = "notebook"
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(
                x=data["data"][0],
                y=data["data"][1],
                mode="lines",
                name=f"Trends {series[0][0:15]}",
                line={"color": "MediumTurquoise", "width": 2.5},
            )
        )
        fig.add_trace(
            go.Scatter(
                x=data["data"][2],
                y=data["data"][3],
                mode="markers",
                name=f"Episodes {series[0][0:15]}",
                line={"color": "DarkTurquoise", "width": 2.5},
            )
        )
        fig.add_trace(
            go.Scatter(
                x=data["data"][4],
                y=data["data"][5],
                line={"color": "DeepPink"},
                name=f"Scores {series[0][0:15]}",
                mode="lines",
                line_shape="spline",
            ),
            secondary_y=True,
        )

        # Second series
        fig.add_trace(
            go.Scatter(
                x=data2["data"][0],
                y=data2["data"][1],
                mode="lines",
                name=f"Trends {series[1][0:15]}",
                line={"color": "MediumSlateBlue", "width": 2.5},
            )
        )
        fig.add_trace(
            go.Scatter(
                x=data2["data"][2],
                y=data2["data"][3],
                mode="markers",
                name=f"Episodes {series[1][0:15]}",
                line={"color": "MediumSlateBlue", "width": 2.5},
            )
        )
        fig.add_trace(
            go.Scatter(
                x=data2["data"][4],
                y=data2["data"][5],
                line={"color": "DarkOrchid"},
                name=f"Scores {series[1][0:15]}",
                mode="lines",
                line_shape="spline",
            ),
            secondary_y=True,
        )
        fig.update_layout(
            # title=f'Trends Comparision: {data["name"]} vs {data2["name"]}',
            xaxis_title="Dates",
            yaxis_title="Trend Value",
            template="plotly_dark",
        )
        st.header(f"Popularity Comparision: {data['name']} vs {data2['name']}")

    fig.update_yaxes(title_text="Score", secondary_y=True)
    return fig

async def main_plots():
    st.title("Anime Plots Comparision")

    button = st.button("Hover over me!")

    # Use an empty element to display the text when hovering
    hover_text = st.empty()

    if button:
        # Show the text when the button is hovered
        hover_text.text("This text appears when you hover over the button!")
        
    query = st.text_input('Enter the anime (seperated by vs)')

    if st.button("Make it happen"):
        fig = await compare_trends(query)
        # print("query", query)
        st.plotly_chart(fig)

if __name__ == "__main__":
    asyncio.run(main_plots())