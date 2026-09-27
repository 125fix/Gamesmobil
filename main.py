import flet as ft
import asyncio
import websockets
import json

async def main(page: ft.Page):
    # Настройки окна приложения
    page.title = "Clicker Game"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#1E1E2E" # Стильный темный фон
    
    score = 0
    username = "player1" # Имя игрока (потом можно сделать поле ввода)
    websocket_conn = None
    
    # Элементы интерфейса
    title_text = ft.Text(
        value="СКОР",
        size=20,
        color="#A6ACCD",
        weight=ft.FontWeight.W_500
    )
    
    score_text = ft.Text(
        value=str(score),
        size=80,
        weight=ft.FontWeight.BOLD,
        color=ft.colors.WHITE
    )

    # Анимация пружинящего нажатия
    async def animate_coin():
        coin.scale = 0.85
        page.update()
        await asyncio.sleep(0.1)
        coin.scale = 1.0
        page.update()

    async def on_click(e):
        # Запускаем анимацию без блокировки
        page.run_task(animate_coin)
        
        # Отправляем клик на сервер, если есть подключение
        if websocket_conn and websocket_conn.open:
            try:
                await websocket_conn.send("click")
            except Exception as ex:
                print("Ошибка отправки клика:", ex)

    # Красивая градиентная кнопка (монета)
    coin = ft.Container(
        content=ft.Text("TAP", size=54, weight=ft.FontWeight.W_900, color=ft.colors.WHITE),
        alignment=ft.alignment.center,
        width=220,
        height=220,
        border_radius=110, # Делаем полностью круглым
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=["#FF0076", "#FF5900"] # Неоновый розово-оранжевый градиент
        ),
        on_click=on_click,
        scale=ft.transform.Scale(1.0),
        # Настраиваем плавность возвращения кнопки в исходный размер
        animate_scale=ft.animation.Animation(150, ft.AnimationCurve.EASE_OUT_BACK) 
    )
    
    # Добавляем всё на экран
    page.add(
        ft.Column(
            controls=[
                title_text,
                score_text,
                ft.Container(height=50), # Отступ между счетом и кнопкой
                coin
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

    # Фоновая задача для подключения к серверу по WebSocket
    async def connect_ws():
        nonlocal websocket_conn, score
        uri = f"ws://localhost:8000/ws/{username}"
        while True:
            try:
                async with websockets.connect(uri) as ws:
                    websocket_conn = ws
                    print("Успешно подключились к серверу!")
                    while True:
                        response = await ws.recv()
                        data = json.loads(response)
                        if data.get("type") == "score_update":
                            score = data.get("score", 0)
                            score_text.value = str(score)
                            page.update()
            except Exception as ex:
                print(f"Отключение от сервера, пробуем снова через 3 сек... Ошибка: {ex}")
                websocket_conn = None
                await asyncio.sleep(3)

    # Запускаем коннект в фоне
    page.run_task(connect_ws)

# Запуск приложения
ft.app(target=main)
