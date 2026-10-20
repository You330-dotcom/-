from flask import Flask, request, redirect, render_template_string
import json
import os

app = Flask(__name__)

DATA_FILE = "favorites.json"
UPLOAD_FOLDER = "static"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# JSON初期化
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False)

def load_cards():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_cards(cards):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)

# 文明
civilizations = ["火", "水", "自然", "闇", "光", "多色"]

civ_colors = {
    "火": "#ff4d4d",
    "水": "#4d79ff",
    "自然": "#4dff4d",
    "闇": "#333333",
    "光": "#fff14d",
    "多色": "#b366ff"
}

# 種類（ボタン）
card_types = ["クリーチャー", "呪文", "フィールド", "タマシード", "その他"]

# コスト
cost_list = list(range(1, 21))

# 種族一覧
def get_races():
    cards = load_cards()
    return sorted(list({c["race"] for c in cards}))

# 編集ページ
html_edit = """
<h1>カードを編集</h1>

<form method="POST" enctype="multipart/form-data">

    <input name="name" value="{{ card.name }}" placeholder="カード名" required><br><br>

    <input type="hidden" name="cost" id="cost_value" value="{{ card.cost }}">
    <input type="hidden" name="civilization" id="civ_value" value="{{ card.civilization }}">
    <input type="hidden" name="type" id="type_value" value="{{ card.type }}">

    <h3>コストを選択</h3>
    {% for n in cost_list %}
        <button type="button"
            onclick="document.getElementById('cost_value').value='{{ n }}'"
            style="padding:10px 15px; margin:5px; background:#555; color:white; border-radius:8px;">
            {{ n }}
        </button>
    {% endfor %}

    <br><br>

    <input name="race" value="{{ card.race }}" placeholder="種族" required><br><br>

    <h3>種類を選択</h3>
    {% for t in card_types %}
        <button type="button"
            onclick="document.getElementById('type_value').value='{{ t }}'"
            style="padding:10px 20px; margin:5px; background:#444; color:white; border-radius:8px;">
            {{ t }}
        </button>
    {% endfor %}

    <br><br>

    <h3>文明を選択</h3>
    {% for c in civilizations %}
        <button type="button"
            onclick="document.getElementById('civ_value').value='{{ c }}'"
            style="padding:10px 20px; margin:5px; background:{{ civ_colors[c] }}; color:white; border-radius:8px;">
            {{ c }}
        </button>
    {% endfor %}

    <br><br>

    <input name="count" value="{{ card.count }}" placeholder="枚数" required><br><br>

    <h3>画像を変更（任意）</h3>
    {% if card.image %}
        <img src="{{ card.image }}" style="width:120px; border-radius:8px;"><br>
    {% endif %}
    <input type="file" name="image"><br><br>

    <button type="submit">保存する</button>

</form>

<br>
<a href="/" style="color:blue;">戻る</a>
"""

# 一覧ページ
html_list = """
<h1>カード一覧</h1>

<!-- 名前検索 + 種族検索 -->
<form method="GET" action="/" style="margin-bottom:10px;">
    <input name="q" placeholder="カード名で検索" value="{{ query }}" 
           style="padding:8px; width:200px;">

    <input name="race" placeholder="種族で検索" value="{{ race_query }}"
           style="padding:8px; width:200px; margin-left:10px;">

    <button type="submit" style="padding:8px;">検索</button>
</form>

<!-- 文明検索（検索条件を引き継ぐ） -->
<div style="margin-bottom:15px;">
    <span>文明で絞り込み：</span>
    {% for c in civilizations %}
        <a href="/?civ={{ c }}&q={{ query }}&race={{ race_query }}&type={{ type_query }}"
           style="padding:6px 12px; margin:3px; background:{{ civ_colors[c] }}; color:white; border-radius:6px;">
           {{ c }}
        </a>
    {% endfor %}

    <a href="/?q={{ query }}&race={{ race_query }}&type={{ type_query }}"
       style="padding:6px 12px; margin:3px; background:#888; color:white; border-radius:6px;">
       全部
    </a>
</div>

<!-- 種類ボタン -->
<div style="margin-bottom:15px;">
    <span>種類で絞り込み：</span>
    {% for t in card_types %}
        <a href="/?type={{ t }}&q={{ query }}&race={{ race_query }}&civ={{ civ_query }}"
           style="padding:6px 12px; margin:3px; background:#444; color:white; border-radius:6px;">
           {{ t }}
        </a>
    {% endfor %}
</div>

<!-- 画像拡大モーダル -->
<div id="imgModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%;
    background:rgba(0,0,0,0.8); justify-content:center; align-items:center;">
    <img id="modalImg" style="max-width:90%; max-height:90%; border-radius:10px;">
</div>

<script>
function showImage(src) {
    document.getElementById("modalImg").src = src;
    document.getElementById("imgModal").style.display = "flex";
}
document.getElementById("imgModal").onclick = function() {
    this.style.display = "none";
};
</script>

<ul>
{% for c in cards %}
    <li style="background:white; padding:10px; margin-top:10px; border-radius:8px;
               border-left:10px solid {{ civ_colors[c.civilization] }};">

        <b>{{ c.name }}</b><br>

        {% if c.image %}
            <img src="{{ c.image }}" onclick="showImage('{{ c.image }}')" 
                 style="width:120px; border-radius:8px; cursor:pointer;"><br>
        {% endif %}

        種類：{{ c.type }}<br>
        コスト：{{ c.cost }} / 種族：{{ c.race }} /
        <span style="color:{{ civ_colors[c.civilization] }};">文明：{{ c.civilization }}</span><br>

        枚数：{{ c.count }} 枚

        <a href="/inc/{{ loop.index0 }}" 
           style="padding:5px 10px; background:#4CAF50; color:white; border-radius:5px; margin-left:10px;">
           ＋
        </a>

        <a href="/dec/{{ loop.index0 }}" 
           style="padding:5px 10px; background:#f44336; color:white; border-radius:5px; margin-left:5px;">
           －
        </a>

        <a href="/edit/{{ loop.index0 }}" 
           style="padding:5px 10px; background:#2196F3; color:white; border-radius:5px; margin-left:10px;">
           編集
        </a>

        <a href="/delete/{{ loop.index0 }}" style="color:red; float:right;">削除</a>
    </li>
{% endfor %}
</ul>

<a href="/add" class="add-button">カードを追加</a>

<style>
a { text-decoration: none; }

.add-button {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #007bff;
    color: white;
    padding: 15px 20px;
    border-radius: 50px;
    text-decoration: none;
    font-weight: bold;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}
</style>
"""

# 追加ページ
html_add = """
<h1>カードを追加</h1>

<form method="POST" enctype="multipart/form-data">

    <input name="name" placeholder="カード名" required><br><br>

    <input type="hidden" name="cost" id="cost_value">
    <input type="hidden" name="civilization" id="civ_value">
    <input type="hidden" name="type" id="type_value">

    <h3>コストを選択</h3>
    {% for n in cost_list %}
        <button type="button"
            onclick="document.getElementById('cost_value').value='{{ n }}'"
            style="padding:10px 15px; margin:5px; background:#555; color:white; border-radius:8px;">
            {{ n }}
        </button>
    {% endfor %}

    <br><br>

    <input name="race" placeholder="種族" required><br><br>

    <h3>種類を選択</h3>
    {% for t in card_types %}
        <button type="button"
            onclick="document.getElementById('type_value').value='{{ t }}'"
            style="padding:10px 20px; margin:5px; background:#444; color:white; border-radius:8px;">
            {{ t }}
        </button>
    {% endfor %}

    <br><br>

    <h3>文明を選択</h3>
    {% for c in civilizations %}
        <button type="button"
            onclick="document.getElementById('civ_value').value='{{ c }}'"
            style="padding:10px 20px; margin:5px; background:{{ civ_colors[c] }}; color:white; border-radius:8px;">
            {{ c }}
        </button>
    {% endfor %}

    <br><br>

    <input name="count" placeholder="枚数" required><br><br>

    <h3>カード画像を選択</h3>
    <input type="file" name="image"><br><br>

    <button type="submit">登録する</button>

</form>

<br>
<a href="/" style="color:blue;">戻る</a>
"""

@app.route("/")
def home():
    cards = load_cards()

    # 古いカードに type が無い場合の安全処理
    for c in cards:
        if "type" not in c:
            c["type"] = ""

    # 名前検索
    query = request.args.get("q", "")
    if query:
        cards = [c for c in cards if query.lower() in c["name"].lower()]

    # 文明検索
    civ_query = request.args.get("civ", "")
    if civ_query:
        cards = [c for c in cards if c["civilization"] == civ_query]

    # 種族検索
    race_query = request.args.get("race", "")
    if race_query:
        cards = [c for c in cards if race_query.lower() in c["race"].lower()]

    # 種類検索
    type_query = request.args.get("type", "")
    if type_query:
        cards = [c for c in cards if type_query.lower() in c["type"].lower()]

    # 並べ替え（コスト → 枚数）
    def safe_int(v, d):
        try:
            return int(v)
        except:
            return d

    cards = sorted(cards, key=lambda x: (safe_int(x["cost"], 999), -safe_int(x["count"], 0)))

    return render_template_string(
        html_list,
        cards=cards,
        civ_colors=civ_colors,
        civilizations=civilizations,
        card_types=card_types,
        races=get_races(),
        query=query,
        race_query=race_query,
        type_query=type_query,
        civ_query=civ_query
    )

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        cards = load_cards()

        image_file = request.files.get("image")
        image_path = None
        if image_file and image_file.filename:
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], image_file.filename)
            image_file.save(save_path)
            image_path = "/" + save_path

        new_card = {
            "name": request.form["name"],
            "cost": request.form.get("cost"),
            "race": request.form["race"],
            "type": request.form.get("type"),
            "civilization": request.form.get("civilization"),
            "count": int(request.form["count"]),
            "image": image_path
        }

        cards.append(new_card)
        save_cards(cards)
        return redirect("/")

    return render_template_string(
        html_add,
        civilizations=civilizations,
        cost_list=cost_list,
        card_types=card_types,
        civ_colors=civ_colors
    )

@app.route("/edit/<int:index>", methods=["GET", "POST"])
def edit(index):
    cards = load_cards()
    card = cards[index]

    if request.method == "POST":
        image_file = request.files.get("image")
        image_path = card["image"]

        if image_file and image_file.filename:
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], image_file.filename)
            image_file.save(save_path)
            image_path = "/" + save_path

        card["name"] = request.form["name"]
        card["cost"] = request.form.get("cost")
        card["race"] = request.form["race"]
        card["type"] = request.form.get("type")
        card["civilization"] = request.form.get("civilization")
        card["count"] = int(request.form["count"])
        card["image"] = image_path

        save_cards(cards)
        return redirect("/")

    return render_template_string(
        html_edit,
        card=card,
        civilizations=civilizations,
        card_types=card_types,
        cost_list=cost_list,
        civ_colors=civ_colors
    )

@app.route("/inc/<int:index>")
def inc(index):
    cards = load_cards()
    cards[index]["count"] = int(cards[index]["count"]) + 1
    save_cards(cards)
    return redirect("/")

@app.route("/dec/<int:index>")
def dec(index):
    cards = load_cards()
    cards[index]["count"] = max(0, int(cards[index]["count"]) - 1)
    save_cards(cards)
    return redirect("/")

@app.route("/delete/<int:index>")
def delete(index):
    cards = load_cards()
    cards.pop(index)
    save_cards(cards)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
