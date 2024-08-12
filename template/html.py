# ----------------------- CUSTOMIZED HTML COMPONENTS ------------------------------

POPUP = """
    <div style="background-color: #ecf0f1;border-radius: 10px;padding: 20px;">
        <div style="align-items:center;display: flex; justify-content:center;">
            <img src="{}"><br>
        </div>
        <b>{}</b><br>
        <i style="font-size:10px;">{}</i><br>
        <hr>
        <div style="align-items:center;display: flex;">
            <button style="align-items: center;border: 0;border-radius: 100px;
            box-sizing: border-box;color: #ffffff;display: inline-flex;
            font-weight: 600;justify-content: center;padding: 0px;
            padding-left: 20px;padding-right: 20px;text-align: center;
            vertical-align: middle;min-height: 30px;background-color: #c1121f;margin:auto;">{} ⭐</button>
            
            <button style="align-items: center;border: 0;border-radius: 100px;
            box-sizing: border-box;color: #ffffff;display: inline-flex;
            font-weight: 600;justify-content: center;padding: 0px;
            padding-left: 20px;padding-right: 20px;text-align: center;
            vertical-align: middle;min-height: 30px;background-color: #c1121f;margin:auto;">{} 👤</button>
            
            <a style="align-items: center;border: 0;border-radius: 100px;
            box-sizing: border-box;color: #ffffff;display: inline-flex;
            font-weight: 600;justify-content: center;padding: 0px; text-decoration: none;
            padding-left: 20px;padding-right: 20px;text-align: center;
            vertical-align: middle;min-height: 30px;background-color: #c1121f;margin:auto;"
            href='tel:{}'">📞</a>
        </div>
    </div>
"""


def card_view(name, address, rating, reviews, contact):
    return f"""
        <div>
            <div>
                <div style='font-size:1.5rem;'><b>{name}</b></div>
                <div style='color:#e63946;'><b>{address}</b></div>
            </div>
            <br>
            <div style="align-items:center;display: flex;">
                <button style='background-color: #4a5759;border: 0;border-radius: 56px;
                                color: #fff;display: inline-block;
                                font-size: 15px; fontweight: 600; outline: 0; padding: 10px 18px; position: relative; 
                                text-align: center; text-decoration: none; transition: all .3s; user-select: none; 
                                -webkit-user-select: none; touch-action: manipulation;margin-right:15px;width:25%;'>
                        {rating} ⭐
                </button>
                <button style='background-color: #4a5759;border: 0;border-radius: 56px;
                                color: #fff;display: inline-block;
                                font-size: 15px; fontweight: 600; outline: 0; padding: 10px 18px; position: relative; 
                                text-align: center; text-decoration: none; transition: all .3s; user-select: none; 
                                -webkit-user-select: none; touch-action: manipulation;margin-right:15px;width:25%;'>
                        {int(reviews)} 👥
                </button>
                <a style='background-color: #4a5759;border: 0;border-radius: 56px;
                                color: #fff;cursor: pointer;display: inline-block;
                                font-size: 15px; fontweight: 600; outline: 0; padding: 10px 18px; position: relative; 
                                text-align: center; text-decoration: none; transition: all .3s; user-select: none; 
                                margin-right:15px;width:25%;'href='tel:{contact}'">
                  Dial 🌐
                </a>
            </div>
        </div>
        """


def review_card(name, date, stars):
    return f"""
        <div>
            <div style="align-items:center;display: flex;justify-content: space-between;">
                <div style="display: inline-block;">
                    <div style='font-size:1.5rem;'><b>{name}</b></div>
                    <div style='color:#415a77;'><b>{date}</b></div>
                </div>
                <button style='background-color: #4a5759;border: 0;border-radius: 56px;
                                color: #fff;display: inline-block;
                                font-size: 13px; fontweight: 600; outline: 0; padding: 8px 18px; position: relative; 
                                text-align: center; text-decoration: none; user-select: none; width:20%;'>
                        {stars} ⭐
                </button>
            </div>
        </div>
        """