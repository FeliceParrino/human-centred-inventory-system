from database import get_connection


def ensure_category_schema():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS category (
            categoryID int NOT NULL AUTO_INCREMENT,
            name varchar(45) NOT NULL,
            userID int NOT NULL,
            PRIMARY KEY (categoryID),
            UNIQUE KEY category_user_unique (name, userID),
            KEY fk_category_user (userID),
            CONSTRAINT fk_category_user FOREIGN KEY (userID) REFERENCES `user` (userID)
        )
    ''')
    cursor.execute("SHOW COLUMNS FROM product LIKE 'categoryID'")
    has_category_column = cursor.fetchone()
    if not has_category_column:
        cursor.execute('ALTER TABLE product ADD categoryID int NULL')
        cursor.execute('ALTER TABLE product ADD KEY fk_product_category (categoryID)')

    cursor.execute("SHOW COLUMNS FROM product LIKE 'costPrice'")
    if not cursor.fetchone():
        cursor.execute('ALTER TABLE product ADD costPrice decimal(10,2) NOT NULL DEFAULT 0')

    cursor.execute("SHOW COLUMNS FROM product LIKE 'salePrice'")
    if not cursor.fetchone():
        cursor.execute('ALTER TABLE product ADD salePrice decimal(10,2) NOT NULL DEFAULT 0')

    cursor.execute("SHOW COLUMNS FROM transaction LIKE 'totalValue'")
    if not cursor.fetchone():
        cursor.execute('ALTER TABLE transaction ADD totalValue decimal(10,2) NOT NULL DEFAULT 0')

    conn.commit()
    cursor.close()
    conn.close()


def ensure_user_privacy_schema():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    user_columns = {
        'email': 'ALTER TABLE `user` ADD email varchar(255) NULL',
        'fullName': 'ALTER TABLE `user` ADD fullName varchar(120) NULL',
        'businessName': 'ALTER TABLE `user` ADD businessName varchar(120) NULL',
        'businessType': 'ALTER TABLE `user` ADD businessType varchar(80) NULL',
        'privacyConsent': 'ALTER TABLE `user` ADD privacyConsent tinyint(1) NOT NULL DEFAULT 0',
        'privacyConsentAt': 'ALTER TABLE `user` ADD privacyConsentAt datetime NULL',
        'privacyNoticeVersion': 'ALTER TABLE `user` ADD privacyNoticeVersion varchar(45) NULL'
    }

    for column, statement in user_columns.items():
        cursor.execute(f"SHOW COLUMNS FROM `user` LIKE '{column}'")
        if not cursor.fetchone():
            cursor.execute(statement)

    cursor.execute("SHOW INDEX FROM `user` WHERE Key_name = 'email_UNIQUE'")
    if not cursor.fetchone():
        cursor.execute('ALTER TABLE `user` ADD UNIQUE KEY email_UNIQUE (email)')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_reset (
            resetID int NOT NULL AUTO_INCREMENT,
            userID int NOT NULL,
            tokenHash varchar(260) NOT NULL,
            expiresAt datetime NOT NULL,
            usedAt datetime NULL,
            createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (resetID),
            KEY fk_password_reset_user (userID),
            CONSTRAINT fk_password_reset_user FOREIGN KEY (userID) REFERENCES `user` (userID)
        )
    ''')

    conn.commit()
    cursor.close()
    conn.close()
