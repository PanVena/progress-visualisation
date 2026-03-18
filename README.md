## Візуалізація поступу перекладу спілки "Ліниві ШІ"

<p align="center">
  <b>Головний інтерфейс (Aurora Theme)</b><br>
  <img src="assets/screenshots/statystyka_fancy.png" width="100%">
</p>

<p align="center">
  <img src="assets/screenshots/statystyka.png" width="49%">
  <img src="assets/screenshots/statystyka_old.png" width="49%">
</p>

<p align="center">
  <img src="assets/screenshots/editor_fancy.png" width="49%">
  <img src="assets/screenshots/editor.png" width="49%">
</p>

# Для особистого використання

* Завантажте сирцевий код собі на пк.
* Встановіть Python з офіційної сторінки.
* Під час інсталяції оберіть: **Додати до PATH**.
* Після, відкриваєм командний рядок з теки з програмою.
* Далі вписуємо <code>pip install -r requirements.txt</code>, за відсутності <code>pip</code> пишемо: <code>python install pip</code>.
* Потім пишемо <code>python main.py</code> .

* Опис ключів у <code>data.json</code>:
  * <code>game</code> - назва гри.
  * <code>icon</code> - шлях до будь якого зображення, може бути як у теці <code>icons</code> так і будь-де на пк, головне подати правильне посилання.
  * <code>sections</code> - розділ, що перелічує у собі всі стовпці підгруп перекладу.
    * <code>name</code> - назва підгрупи (текст, DLC, досягнення, текстури, озвучка).
    * <code>translated_label</code> і <code>approved_label</code> - змінні, які дають вам можливість змінити записи <code>Перекладено</code> і <code>Затверджено</code> у підгрупах.
    * <code>total</code> - загальна кількість слів/рядків у підгрупі.
    * <code>translated</code> - перекладена кількість слів/рядків у підгрупі.
    * <code>approved</code> - затверджена кількість слів/рядків у підгрупі.
    * <code>exclude_from_total</code> - якщо має статус <code>true</code> ця підгрупа не буде врахована у загальному підрахунку проєкту.
  

<h1 align="center"> <a href="https://t.me/linyvi_sh_ji"><b>Спілка "Ліниві ШІ"</b></a></h1>

