# Copyright (C) 2026 Oktapiancaw
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
from datetime import datetime, timedelta

from sqlalchemy import func, select
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from src.configs import project_meta
from src.model.meta import BillingMethod, Category, SessionLocal, Transaction

AMOUNT, TYPE, CATEGORY, BILLING, DESCRIPTION = range(5)
LOGGER = logging.getLogger(project_meta.name)


def format_rupiah(amount: float) -> str:
    """Formats a float into an Indonesian Rupiah string (e.g., Rp 15.000)."""
    return f"Rp {int(amount):,}".replace(",", ".")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    pesan = (
        f"Halo Bosku *{user.first_name}*! 👋 Welcome ke Bot Keuangan Anti-Boncos!\n\n"
        f"Aku di sini buat bantuin kamu nyatet duit masuk dan duit melayang biar nggak tiba-tiba miskin di akhir bulan. 💸\n\n"
        f"Langsung aja ketik /help buat liat daftar jurus rahasia yang bisa aku lakuin ya! 🚀"
    )
    await update.message.reply_text(pesan, parse_mode=ParseMode.MARKDOWN)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pesan = (
        "🛠 *Buku Panduan Bertahan Hidup (Finansial)* 📖\n\n"
        "Ini dia daftar perintah yang bisa kamu ketik:\n\n"
        "📝 *Pencatatan Harian*\n"
        "🔹 /log - Mulai nyatet transaksi (pemasukan/pengeluaran). Jangan ditunda-tunda!\n"
        "🔹 /cancel - Batalin pencatatan kalau tiba-tiba sadar salah ketik.\n\n"
        "⚙️ *Pengaturan Dompet & Kategori*\n"
        "🔹 `/addcat <masuk/keluar> <nama>` - Bikin kategori baru.\n"
        "      _Contoh: `/addcat keluar Kopi Janji Manis`_\n"
        "🔹 `/addbill <nama>` - Tambah dompet/metode bayar baru.\n"
        "      _Contoh: `/addbill Kartu Kredit BCA`_\n\n"
        "📊 *Cek Realita (Laporan)*\n"
        "🔹 /daily - Laporan hari ini. Berani liat?\n"
        "🔹 /weekly - Rekap seminggu ke belakang.\n"
        "🔹 /monthly - Laporan bulanan. Momen penentuan kamu kaya atau miskin. 🫣\n\n"
        "_Yuk, mulai catat keuanganmu dari sekarang!_"
    )
    await update.message.reply_text(pesan, parse_mode=ParseMode.MARKDOWN)


async def add_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        pesan_error = (
            "Waduh, formatnya kurang lengkap Bos! 😅\n"
            "Ketik: `/addcat <masuk/keluar> <nama_kategori>`\n\n"
            "*Contoh:*\n"
            "`/addcat keluar Kopi Janji Manis`\n"
            "`/addcat masuk Gaji Bulanan`"
        )
        await update.message.reply_text(pesan_error, parse_mode=ParseMode.MARKDOWN)
        return
    cat_type = context.args[0].lower()
    if cat_type not in ["masuk", "keluar"]:
        await update.message.reply_text(
            "Tipe kategorinya cuma bisa *masuk* atau *keluar* ya! 🙅‍♂️ Jangan ngarang ah.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    name = " ".join(context.args[1:])
    user_id = update.effective_user.id
    with SessionLocal() as session:
        existing = session.scalar(
            select(Category).where(
                Category.name == name,
                Category.user_id == user_id,
                Category.category_type == cat_type,
            )
        )
        if existing:
            await update.message.reply_text(
                f"Kategori *{name}* udah ada! Jangan dobel-dobel dong. 🧐",
                parse_mode=ParseMode.MARKDOWN,
            )
            return
        session.add(Category(name=name, user_id=user_id, category_type=cat_type))
        session.commit()
    icon = "💰" if cat_type == "masuk" else "💸"
    await update.message.reply_text(
        f"Mantap! {icon} Kategori *{name}* (Tipe: {cat_type.upper()}) udah aman di database!",
        parse_mode=ParseMode.MARKDOWN,
    )


async def add_billing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Metode bayarnya gaib nih? 👻 Ketik `/addbill <nama_dompet>` dong!",
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    name = " ".join(context.args)
    user_id = update.effective_user.id
    with SessionLocal() as session:
        existing = session.scalar(
            select(BillingMethod).where(
                BillingMethod.name == name, BillingMethod.user_id == user_id
            )
        )
        if existing:
            await update.message.reply_text(
                f"Metode Bayar '{name}'. Udah ada cuy, coba ganti yang lain."
            )
            return
        session.add(BillingMethod(name=name, user_id=user_id))
        session.commit()
    await update.message.reply_text(
        f"Asik! 💳 Dompet *{name}* udah siap dikuras... eh, dipake!",
        parse_mode=ParseMode.MARKDOWN,
    )


async def log_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "Siap mencatat pengeluaran! 💸\n*Habis jajan berapa nih hari ini?* (Tulis angkanya aja ya, misal: 50000)",
            parse_mode=ParseMode.MARKDOWN,
        )
        return AMOUNT
    except Exception as e:
        LOGGER.error(f"💥 Waduh, bot-nya nyungsep di log_start: {e}")
        raise e


async def log_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["amount"] = float(update.message.text)
    except ValueError:
        await update.message.reply_text(
            "Hadeh, itu mah huruf, Bang! 🤦‍♂️ Tulis *angka* yang bener dong.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return AMOUNT

    reply_keyboard = [["🟢 Pemasukan", "🔴 Pengeluaran"]]

    await update.message.reply_text(
        "Oke, ini ceritanya duit nambah atau duit melayang nih? 🤔",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        parse_mode=ParseMode.MARKDOWN,
    )
    return TYPE


async def log_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pilihan_user = update.message.text.lower()

    if "pemasukan" in pilihan_user:
        cat_type = "masuk"
    elif "pengeluaran" in pilihan_user:
        cat_type = "keluar"
    else:
        await update.message.reply_text(
            "Pencet tombol yang ada di layar aja ya Bosku! 🟢 atau 🔴",
            parse_mode=ParseMode.MARKDOWN,
        )
        return TYPE

    context.user_data["cat_type"] = cat_type
    user_id = update.effective_user.id

    with SessionLocal() as session:
        categories = session.scalars(
            select(Category).where(
                Category.user_id == user_id, Category.category_type == cat_type
            )
        ).all()

        if not categories:
            await update.message.reply_text(
                f"Waduh, belum ada kategori buat tipe *{cat_type.upper()}*! 🏜️\n"
                f"Batalin dulu pakai `/cancel`, terus bikin pakai `/addcat {cat_type} <nama>` ya.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=ReplyKeyboardRemove(),
            )
            return ConversationHandler.END

        reply_keyboard = [[c.name] for c in categories]
        print(reply_keyboard)

    await update.message.reply_text(
        f"Sip! Buat kategori *{cat_type.upper()}* yang mana nih? 🛒",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        parse_mode=ParseMode.MARKDOWN,
    )
    return CATEGORY


async def log_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["category"] = update.message.text

    user_id = update.effective_user.id
    with SessionLocal() as session:
        billing_methods = session.scalars(
            select(BillingMethod).where(BillingMethod.user_id == user_id)
        ).all()
        if not billing_methods:
            await update.message.reply_text(
                "Bayarnya pake daun? 🍃 Tambahin metode pembayaran dulu pake `/addbill` ya.",
                parse_mode=ParseMode.MARKDOWN,
            )
            return ConversationHandler.END

        reply_keyboard = [[b.name] for b in billing_methods]

    await update.message.reply_text(
        "Bayarnya pake dompet yang mana nih? 💳 Tarik sis!",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return BILLING


async def log_billing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["billing"] = update.message.text
    await update.message.reply_text(
        "Sip! Terakhir, kasih *deskripsi singkat* dong biar nggak lupa ✍️\n_(misal: 'Beli kopi janji manis')_",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode=ParseMode.MARKDOWN,
    )
    return DESCRIPTION


async def log_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    description = update.message.text
    data = context.user_data
    user_id = update.effective_user.id

    with SessionLocal() as session:
        cat = session.scalar(
            select(Category).where(
                Category.name == data["category"], Category.user_id == user_id
            )
        )
        bill = session.scalar(
            select(BillingMethod).where(
                BillingMethod.name == data["billing"], BillingMethod.user_id == user_id
            )
        )

        transaction = Transaction(
            amount=data["amount"],
            user_id=user_id,
            description=description,
            category_id=cat.id,
            billing_method_id=bill.id,
        )
        session.add(transaction)
        session.commit()

        category_name = cat.name
        billing_name = bill.name

    formatted_amount = format_rupiah(data["amount"])
    receipt_message = (
        f"✅ *Sip, udah kecatat!*\n\n"
        f"💸 *Nominal:* {formatted_amount}\n"
        f"📝 *Catatan:* {description}\n"
        f"🏷 *Kategori:* {category_name}\n"
        f"💳 *Dompet:* {billing_name}\n\n"
        f"_Semoga bulan ini nggak cepet miskin ya!_ 🤪"
    )

    await update.message.reply_text(receipt_message, parse_mode=ParseMode.MARKDOWN)
    context.user_data.clear()
    return ConversationHandler.END


async def log_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Yaudah deh, gajadi nyatet. 🙅‍♂️ Duitnya aman terselamatkan!",
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data.clear()
    return ConversationHandler.END


async def generate_report(
    update: Update, context: ContextTypes.DEFAULT_TYPE, days: int, title: str
):
    time_threshold = datetime.utcnow() - timedelta(days=days)
    user_id = update.effective_user.id

    with SessionLocal() as session:
        results = session.execute(
            select(Category.name, Category.category_type, func.sum(Transaction.amount))
            .join(Transaction)
            .where(
                Transaction.timestamp >= time_threshold, Transaction.user_id == user_id
            )
            .group_by(Category.name, Category.category_type)
        ).all()

    if not results:
        await update.message.reply_text(
            f"Wah, kuburan sepi nih! 🕸️ Nggak ada mutasi saldo buat laporan *{title}* ini.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    title_id = {"Daily": "Harian", "Weekly": "Mingguan", "Monthly": "Bulanan"}.get(
        title, title
    )

    total_masuk = 0
    total_keluar = 0
    masuk_text = "🟢 *PEMASUKAN:*\n"
    keluar_text = "🔴 *PENGELUARAN:*\n"

    for cat_name, cat_type, amount in results:
        if cat_type == "masuk":
            masuk_text += f"➕ {cat_name}: {format_rupiah(amount)}\n"
            total_masuk += amount
        else:
            keluar_text += f"➖ {cat_name}: {format_rupiah(amount)}\n"
            total_keluar += amount

    report = f"📊 *Laporan Keuangan ({title_id})* 📈\n\n"
    if total_masuk > 0:
        report += masuk_text + "\n"
    if total_keluar > 0:
        report += keluar_text + "\n"

    net = total_masuk - total_keluar
    status_keuangan = (
        "Aman Bos, cuan melimpah! 🏖️"
        if net >= 0
        else "Besar pasak dari tiang nih, awas boncos! 🚨"
    )

    report += "====================\n"
    report += f"💵 *Total Masuk:* {format_rupiah(total_masuk)}\n"
    report += f"🔥 *Total Keluar:* {format_rupiah(total_keluar)}\n"
    report += f"⚖️ *Sisa / Selisih:* *{format_rupiah(net)}*\n\n_{status_keuangan}_"

    await update.message.reply_text(report, parse_mode=ParseMode.MARKDOWN)


async def report_daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await generate_report(update, context, days=1, title="Daily")


async def report_weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await generate_report(update, context, days=7, title="Weekly")


async def report_monthly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await generate_report(update, context, days=30, title="Monthly")
