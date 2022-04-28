<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:template match="/">

        <html>
            <head><link rel="stylesheet" type="text/css" href="http://localhost/pages/css/diktbase.css" /></head>
            <body>
                <h1>Diktbase</h1>
                <table border="1">
                    <tr>
                        <th>Id</th><th>Dikt</th><th>Eier</th>
                    </tr>

                    <xsl:for-each select="diktbase/Dikt">
                        <xsl:sort select="diktID"/>
                        <tr>
                            <td><xsl:value-of select="diktID"/></td>
                            <td><xsl:value-of select="tekst"/></td>
                            <td><xsl:value-of select="epost"/></td>
                        </tr>
                    </xsl:for-each>
                </table>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
