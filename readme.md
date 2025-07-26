# Instrucciones de Testing - Sistema de Gestión de Empleados

## Requisitos Previos

- Python 3.8 o superior
- Archivo `employee_management_system.py` (código refactorizado)

## Instalación y Ejecución

```bash
# 1. Guardar el código refactorizado en un archivo
# employee_management_system.py

# 2. Ejecutar el sistema
python employee_management_system.py
```

## Escenarios de Testing

### Test 1: Creación de Empleados (Factory Pattern)

**Objetivo**: Verificar que el Factory Pattern crea empleados correctamente.

1. Ejecutar el sistema
2. Seleccionar opción `1. Create employee`
3. **Test 1.1 - Empleado Asalariado**:
   - Nombre: `Juan Perez`
   - Rol: `manager`
   - Tipo: `salaried`
   - Salario: `5000`
   - **Resultado esperado**: Empleado creado exitosamente

4. **Test 1.2 - Empleado por Horas**:
   - Nombre: `Ana Garcia`
   - Rol: `intern`
   - Tipo: `hourly`
   - Tarifa por hora: `25`
   - Horas trabajadas: `180`
   - **Resultado esperado**: Empleado creado exitosamente

5. **Test 1.3 - Freelancer**:
   - Nombre: `Carlos Rodriguez`
   - Rol: `manager`
   - Tipo: `freelancer`
   - **Resultado esperado**: Empleado creado exitosamente

### Test 2: Strategy Pattern - Políticas de Vacaciones

**Objetivo**: Verificar que las políticas de vacaciones funcionan según el rol.

1. **Test 2.1 - Intern (No puede tomar vacaciones)**:
   - Ir a `3. Grant vacation to an employee`
   - Seleccionar `Ana Garcia` (intern)
   - Días: `5`
   - Payout: `n`
   - **Resultado esperado**: Error - "Cannot take 5 vacation days"

2. **Test 2.2 - Manager (Hasta 10 días de payout)**:
   - Seleccionar `Juan Perez` (manager)
   - Días: `8`
   - Payout: `y`
   - **Resultado esperado**: Vacaciones otorgadas exitosamente

3. **Test 2.3 - Manager (Más de 10 días de payout - debe fallar)**:
   - Seleccionar `Juan Perez` (manager)
   - Días: `15`
   - Payout: `y`
   - **Resultado esperado**: Error - "Cannot payout 15 vacation days"

### Test 3: Strategy Pattern - Cálculo de Pagos con Bonificaciones

**Objetivo**: Verificar que el Strategy Pattern calcula pagos y bonificaciones correctamente.

1. Ir a `4. Pay employees`
2. **Resultados esperados**:
   - **Juan Perez (Manager asalariado)**: $5,500.00 (Base: $5,000 + Bonus: $500)
   - **Ana Garcia (Intern por horas)**: $4,500.00 (Solo base, sin bonus por ser intern)
   - **Carlos Rodriguez (Freelancer)**: $0.00 (Sin proyectos aún)

### Test 4: Funcionalidad de Freelancers

**Objetivo**: Verificar gestión de proyectos para freelancers.

1. **Test 4.1 - Agregar Proyecto**:
   - Ir a `5. Add project (Freelancers)`
   - Seleccionar `Carlos Rodriguez`
   - Nombre del proyecto: `Website Development`
   - Monto: `3000`
   - **Resultado esperado**: Proyecto agregado exitosamente

2. **Test 4.2 - Verificar Pago de Freelancer**:
   - Ir a `4. Pay employees`
   - **Resultado esperado**: Carlos Rodriguez debe mostrar $3,000.00

3. **Test 4.3 - Múltiples Proyectos**:
   - Agregar otro proyecto: `Mobile App`, monto: `2500`
   - Pagar empleados nuevamente
   - **Resultado esperado**: Carlos Rodriguez debe mostrar $5,500.00

### Test 5: Command Pattern - Historial de Transacciones

**Objetivo**: Verificar que el Command Pattern registra todas las operaciones.

1. **Test 5.1 - Verificar Historial de Pagos**:
   - Ir a `6. View employee history`
   - Seleccionar `Juan Perez`
   - **Resultado esperado**: Debe mostrar transacciones de tipo "PAYMENT"

2. **Test 5.2 - Verificar Historial de Vacaciones**:
   - Seleccionar `Juan Perez`
   - **Resultado esperado**: Debe mostrar transacción "VACATION_PAYOUT"

### Test 6: Configuración Dinámica

**Objetivo**: Verificar que las reglas de negocio son configurables.

1. **Test 6.1 - Cambiar Configuración**:
   - Ir a `7. Update payroll configuration`
   - Opción `1. Salaried bonus percentage`
   - Nuevo valor: `0.15` (15%)
   - **Resultado esperado**: Configuración actualizada

2. **Test 6.2 - Verificar Nuevo Cálculo**:
   - Ir a `4. Pay employees`
   - **Resultado esperado**: Juan Perez ahora debe recibir $5,750.00 (Base: $5,000 + Bonus: $750)

3. **Test 6.3 - Verificar Persistencia**:
   - Salir del programa (opción `8`)
   - Reiniciar el programa
   - Crear un nuevo empleado asalariado y pagar
   - **Resultado esperado**: Debe usar la nueva configuración (15%)

### Test 7: Visualización por Roles

**Objetivo**: Verificar que la búsqueda por roles funciona correctamente.

1. Ir a `2. View employees`
2. **Test 7.1 - Ver Managers**:
   - Opción `1. View managers`
   - **Resultado esperado**: Debe mostrar Juan Perez y Carlos Rodriguez

3. **Test 7.2 - Ver Interns**:
   - Opción `2. View interns`
   - **Resultado esperado**: Debe mostrar Ana Garcia

4. **Test 7.3 - Ver Freelancers**:
   - Opción `4. View freelancers`
   - **Resultado esperado**: Debe mostrar Carlos Rodriguez con sus proyectos

### Test 8: Casos Edge y Validaciones

**Objetivo**: Verificar manejo de errores y validaciones.

1. **Test 8.1 - Datos Inválidos**:
   - Crear empleado con salario no numérico
   - **Resultado esperado**: Error manejado gracefully

2. **Test 8.2 - Empleado Inexistente**:
   - Intentar otorgar vacaciones con índice inválido
   - **Resultado esperado**: Error manejado

3. **Test 8.3 - Proyecto a No-Freelancer**:
   - Intentar agregar proyecto a empleado asalariado
   - **Resultado esperado**: Error - "Only freelancers can have projects"

## Verificación de Principios SOLID

### Single Responsibility Principle (SRP)
- **Verificar**: Cada clase tiene una responsabilidad clara
- **Ejemplo**: PayrollService solo maneja pagos, VacationService solo vacaciones

### Open/Closed Principle (OCP)
- **Verificar**: Agregar nuevos tipos de empleados no requiere modificar código existente
- **Test**: El sistema permite extensión fácil de nuevas estrategias

### Liskov Substitution Principle (LSP)
- **Verificar**: Todas las estrategias son intercambiables
- **Test**: PaymentStrategy funciona igual independientemente de la implementación

### Interface Segregation Principle (ISP)
- **Verificar**: Interfaces específicas y cohesivas
- **Test**: PaymentStrategy solo tiene métodos de pago

### Dependency Inversion Principle (DIP)
- **Verificar**: Dependencias en abstracciones
- **Test**: Company no depende de implementaciones concretas

## Resultados Esperados del Testing

Al completar todos los tests, deberías verificar:

✅ **Factory Pattern**: Creación correcta de empleados con estrategias apropiadas  
✅ **Strategy Pattern**: Cálculos diferenciados sin condicionales `isinstance()`  
✅ **Command Pattern**: Historial completo de todas las operaciones  
✅ **SOLID Principles**: Código extensible sin modificar existente  
✅ **Configuración Externa**: Reglas modificables dinámicamente  
✅ **Separación de Responsabilidades**: UI desacoplada de lógica de negocio  

## Archivo de Configuración Generado

Durante el testing, se creará automáticamente:
```json
// payroll_config.json
{
  "salaried_bonus_percentage": 0.15,
  "hourly_bonus_threshold": 160,
  "hourly_bonus_amount": 100
}
```

## Troubleshooting

**Problema**: Error al crear empleado  
**Solución**: Verificar que los tipos ingresados sean exactos: `salaried`, `hourly`, `freelancer`

**Problema**: Configuración no persiste  
**Solución**: Verificar permisos de escritura en el directorio actual

**Problema**: Historial vacío  
**Solución**: Ejecutar operaciones (pagos, vacaciones) antes de consultar historial