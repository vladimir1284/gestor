-- Remover las ordenes en storage
-- pone el preorder.order_id en null
DELETE
FROM utils_order
WHERE position = 0;

-- Elimina todas las preorders con order_id en null
DELETE
FROM services_preorder
WHERE order_id is NULL;
