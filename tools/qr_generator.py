import qrcode
import os
from core.logger import logger

async def generate_qr_code(data: str, filename: str = "qrcode.png") -> str:
    """Генерує QR-код з тексту або посилання та зберігає його у файл."""
    logger.info(f"[bold yellow]🔳 Генерація QR-коду для:[/bold yellow] {data}")
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        # Створюємо зображення
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Зберігаємо у поточну робочу папку проєкту
        filepath = os.path.join(os.getcwd(), filename)
        img.save(filepath)
        
        return f"QR-код успішно згенеровано! Файл збережено локально за шляхом: {filepath}"
    except Exception as e:
        logger.error(f"[bold red]❌ Помилка генерації QR:[/bold red] {str(e)}")
        return "Не вдалося згенерувати QR-код."