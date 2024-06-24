# Django query logs

## Summary

| Category  | Value    | SQL                                                                                                                                                                                                                                                                                                                                                               |
| --------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Avg Time  |    0.000 |                                                                                                                                                                                                                                                                                                                                                                   |
| Slower    |    0.002 | `SELECT "django_content_type"."id","django_content_type"."app_label","django_content_type"."model" FROM "django_content_type" WHERE("django_content_type"."app_label" IN(?0,?1,?2,?3)AND "django_content_type"."model"=?4)                                                                                                                                      ` |
| Faster    |    0.000 | `SELECT "template_admin_templateversion"."id","template_admin_templateversion"."module","template_admin_templateversion"."template","template_admin_templateversion"."language","template_admin_templateversion"."tmp_type","template_admin_templateversion"."custom" FROM "template_admin_templateversion" WHERE NOT("template_admin_templateversion"."custom")` |
| Avg Count |     1.00 |                                                                                                                                                                                                                                                                                                                                                                   |
| Max count |        1 | `SELECT "template_admin_templateversion"."id","template_admin_templateversion"."module","template_admin_templateversion"."template","template_admin_templateversion"."language","template_admin_templateversion"."tmp_type","template_admin_templateversion"."custom" FROM "template_admin_templateversion" WHERE NOT("template_admin_templateversion"."custom")` |
| Min count |        1 | `SELECT "template_admin_templateversion"."id","template_admin_templateversion"."module","template_admin_templateversion"."template","template_admin_templateversion"."language","template_admin_templateversion"."tmp_type","template_admin_templateversion"."custom" FROM "template_admin_templateversion" WHERE NOT("template_admin_templateversion"."custom")` |

## Queries

### Query 0 / 9

| Metric   | Value    |
| -------- | -------- |
| Count    |        1 |
| Avg Time |    0.000 |
| Max Time |    0.000 |
| Min Time |    0.000 |

```sql
SELECT "template_admin_templateversion"."id","template_admin_templateversion"."module","template_admin_templateversion"."template","template_admin_templateversion"."language","template_admin_templateversion"."tmp_type","template_admin_templateversion"."custom" FROM "template_admin_templateversion" WHERE NOT("template_admin_templateversion"."custom")
```

### Query 1 / 9

| Metric   | Value    |
| -------- | -------- |
| Count    |        1 |
| Avg Time |    0.000 |
| Max Time |    0.000 |
| Min Time |    0.000 |

```sql
SELECT "auth_permission"."id","auth_permission"."name","auth_permission"."content_type_id","auth_permission"."codename" FROM "auth_permission" INNER JOIN "django_content_type" ON("auth_permission"."content_type_id"="django_content_type"."id")WHERE "auth_permission"."content_type_id" IN(?0,?1,?2,?3)ORDER BY "django_content_type"."app_label" ASC,"django_content_type"."model" ASC,"auth_permission"."codename" ASC
```

### Query 2 / 9

| Metric   | Value    |
| -------- | -------- |
| Count    |        1 |
| Avg Time |    0.001 |
| Max Time |    0.001 |
| Min Time |    0.001 |

```sql
SELECT "auth_permission"."id","auth_permission"."name","auth_permission"."content_type_id","auth_permission"."codename" FROM "auth_permission" WHERE("auth_permission"."content_type_id" IN(?0,?1,?2,?3)AND NOT("auth_permission"."codename" IN(?4,?5,?6,?7,?8,?9,?10,?11,?12,?13,?14,?15,?16,?17,?18,?19,?20,?21,?22,?23,?24,?25,?26,?27,?28,?29,?30,?31,?32,?33,?34,?35,?36,?37,?38,?39,?40,?41,?42,?43,?44,?45,?46,?47,?48,?49,?50,?51,?52,?53,?54,?55,?56,?57,?58,?59,?60,?61,?62,?63,?64,?65,?66,?67,?68,?69,?70,?71,?72,?73,?74,?75,?76,?77,?78,?79,?80,?81,?82,?83,?84,?85,?86,?87,?88,?89,?90,?91,?92,?93,?94,?95,?96,?97,?98,?99,?100,?101,?102,?103,?104,?105,?106,?107,?108,?109,?110,?111,?112,?113,?114,?115,?116,?117,?118,?119,?120,?121,?122,?123,?124,?125,?126,?127,?128,?129,?130,?131,?132,?133,?134,?135,?136,?137,?138,?139,?140,?141,?142,?143,?144,?145,?146,?147,?148,?149,?150,?151,?152,?153,?154,?155,?156,?157,?158,?159,?160,?161,?162,?163,?164,?165,?166,?167,?168,?169,?170,?171,?172,?173,?174,?175,?176,?177,?178,?179,?180,?181,?182,?183,?184,?185,?186,?187,?188,?189,?190,?191,?192,?193,?194,?195,?196,?197,?198,?199,?200,?201,?202,?203,?204,?205,?206,?207,?208,?209,?210,?211,?212,?213,?214,?215,?216,?217,?218,?219,?220,?221,?222,?223,?224,?225,?226,?227,?228,?229,?230,?231,?232,?233,?234,?235,?236,?237,?238,?239,?240,?241,?242,?243,?244,?245,?246,?247,?248,?249,?250,?251,?252,?253,?254,?255,?256,?257,?258,?259,?260,?261,?262,?263,?264,?265,?266,?267,?268,?269,?270,?271,?272,?273,?274,?275,?276,?277,?278,?279,?280,?281,?282,?283,?284,?285,?286,?287,?288,?289,?290,?291,?292,?293,?294,?295,?296,?297,?298,?299,?300,?301,?302,?303,?304,?305,?306,?307,?308,?309,?310,?311,?312,?313,?314,?315,?316,?317,?318,?319,?320,?321,?322,?323,?324,?325,?326,?327,?328,?329,?330,?331,?332)))
```

### Query 3 / 9

| Metric   | Value    |
| -------- | -------- |
| Count    |        1 |
| Avg Time |    0.000 |
| Max Time |    0.000 |
| Min Time |    0.000 |

```sql
SELECT "django_migrations"."id","django_migrations"."app","django_migrations"."name","django_migrations"."applied" FROM "django_migrations"
```

### Query 4 / 9

| Metric   | Value    |
| -------- | -------- |
| Count    |        1 |
| Avg Time |    0.000 |
| Max Time |    0.000 |
| Min Time |    0.000 |

```sql
COMMIT
```

### Query 5 / 9

| Metric   | Value    |
| -------- | -------- |
| Count    |        1 |
| Avg Time |    0.000 |
| Max Time |    0.000 |
| Min Time |    0.000 |

```sql
BEGIN
```

### Query 6 / 9

| Metric   | Value    |
| -------- | -------- |
| Count    |        1 |
| Avg Time |    0.002 |
| Max Time |    0.002 |
| Min Time |    0.002 |

```sql
SELECT "django_content_type"."id","django_content_type"."app_label","django_content_type"."model" FROM "django_content_type" WHERE("django_content_type"."app_label" IN(?0,?1,?2,?3)AND "django_content_type"."model"=?4)
```

### Query 7 / 9

| Metric   | Value    |
| -------- | -------- |
| Count    |        1 |
| Avg Time |    0.001 |
| Max Time |    0.001 |
| Min Time |    0.001 |

```sql
SELECT name,type FROM sqlite_master WHERE type in('table','view')AND NOT name='sqlite_sequence' ORDER BY name
```

### Query 8 / 9

| Metric   | Value    |
| -------- | -------- |
| Count    |        1 |
| Avg Time |    0.000 |
| Max Time |    0.000 |
| Min Time |    0.000 |

```sql
SELECT "template_admin_template"."id","template_admin_template"."module","template_admin_template"."template","template_admin_template"."language","template_admin_template"."tmp_type","template_admin_template"."content" FROM "template_admin_template"
```

