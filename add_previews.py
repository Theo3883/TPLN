"""
Script pentru a adăuga preview text la ediții pentru testare.
"""
import asyncio
import asyncpg

# Database connection
DATABASE_URL = "postgresql://tpln:tpln@localhost:5433/tpln"

SAMPLE_PREVIEWS = [
    """Acesta este un fragment introductiv care prezintă universul cărții. 
    Autorul reușește să creeze o atmosferă captivantă prin descrieri bogate și dialogue autentice. 
    Personajele sunt complexe, bine conturate, iar trama este plină de suspans. 
    O lectură care merită atenția cititorilor pasionați de literatură de calitate.""",
    
    """Fragment fascinant care explorează teme profunde despre existența umană. 
    Stilul narativ este elegant și plin de subtilități care invită la reflecție. 
    Proza curge firesc, captivând cititorul de la prima pagină. 
    O carte care rămâne în memoria cititorului mult timp după terminarea lecturii.""",
    
    """Primele capitole ne introduc într-o poveste captivantă, plină de emoție. 
    Autorul demonstrează o înțelegere profundă a naturii umane prin personajele sale. 
    Narațiunea este bine structurată, cu momente de intensitate și lirism. 
    Recomandată tuturor iubitorilor de literatură autentică și profundă.""",
    
    """Un debut promițător care prezintă o viziune originală asupra temelor abordate. 
    Stilul este fresh, modern, adaptat cititorului contemporan. 
    Dialogurile sunt naturale, iar evoluția personajelor este credibilă. 
    O carte care merită citită și discutată în cercurile literare.""",
    
    """Fragment intrigant care ridică întrebări fundamentale despre condiția umană. 
    Proza este densă, plină de metafore și simboluri care îmbogățesc lectura. 
    Autorul jonglează cu abilitate între real și imaginar, creând un univers unic. 
    O experiență de lectură pe care nu o vei uita ușor.""",
]


async def add_previews():
    """Adaugă preview text la primele 10 ediții."""
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # Get first 10 editions with their book titles
        editions = await conn.fetch("""
            SELECT e.id, b.title 
            FROM editions e
            JOIN books b ON e.book_id = b.id
            WHERE e.preview_text IS NULL
            ORDER BY e.id
            LIMIT 10
        """)
        
        if not editions:
            print("✅ Toate edițiile au deja preview!")
            return
        
        print(f"📚 Adaug preview la {len(editions)} ediții...\n")
        
        for idx, edition in enumerate(editions):
            # Cycle through sample previews
            preview = SAMPLE_PREVIEWS[idx % len(SAMPLE_PREVIEWS)]
            
            # Customize preview with book title
            custom_preview = f'Fragment din "{edition["title"]}":\n\n{preview}'
            
            # Update edition
            await conn.execute(
                "UPDATE editions SET preview_text = $1 WHERE id = $2",
                custom_preview,
                edition["id"]
            )
            
            print(f"✅ Edition #{edition['id']}: {edition['title']}")
        
        print(f"\n✅ Preview-uri adăugate cu succes! Acum poți scrie review-uri pentru {len(editions)} cărți.")
        
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(add_previews())
