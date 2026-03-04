# Логика за показване на "+" пред всяко подасембли (подсборка)

## Основна цел
Всички подасемблита (subassemblies) в дървото на BOM визуализатора да имат бутон "+" (expand), независимо от нивото им или дали са преместени (orphan).

## Ключови стъпки и функции

### 1. Функция getAssemblyChildren
- **Роля:** Разделя децата на дадена сборка на `details` (детайли) и `subassemblies` (подсборки).
- **Логика:**
  - За всяко дете се проверява дали има поддеца (рекурсивно извикване на getAssemblyChildren с visitedPaths защита).
  - Ако има поддеца или fallback (има само едно съвпадение по path), се добавя към `subassemblies` с `isSubassembly: true`.
  - Ако е крепеж (fastener), се добавя към `details`.
  - Ако името съдържа "Komplekt", "Комплект" или "Treger Chassis", също се добавя към `subassemblies` с `isSubassembly: true`.
  - Всички останали са `details`.
- **Важно:**
  - Задължително се пази visitedPaths (Set), който се подава като втори аргумент при всяко рекурсивно извикване, и се добавя текущият parentPath в началото на функцията. Ако parentPath вече е в visitedPaths, функцията връща празни деца (защита от безкрайна рекурсия).

### 2. Рендериране на подсборки
- При рендериране на всяка подсборка (subassembly) към renderAssemblyTreeItem се подава обект с `isSubassembly: true`.
- Това се прави навсякъде, където се рендерират подсборки (вкл. orphan subassemblies).

### 3. Логика за показване на "+"
- Във функцията renderAssemblyTreeItem:
  - Използва се следната логика:
    ```js
    const noExpandNames = ['ALL Kabina stoqshta', 'ALL Pod 1-4', 'ALL Double Shasi', 'Двойно шаси'];
    const isSubassembly = assembly.isSubassembly || assembly.level > 1;
    const showExpandButton = !noExpandNames.includes(assembly.name) && (isSubassembly || isAssembly || hasChildren);
    ```
  - Ако showExpandButton е true, се показва бутон "+" пред подсборката.

### 4. Преместени подсборки (orphan subassemblies)
- При рендериране на orphan подсборки (индивидуално преместени), те се подават към renderAssemblyTreeItem с `isSubassembly: true`, за да се държат като подсборки, а не като детайли.

## Какво да се провери при проблем
- Дали getAssemblyChildren пази и подава visitedPaths коректно.
- Дали всички подсборки се подават към renderAssemblyTreeItem с isSubassembly: true.
- Дали логиката за showExpandButton е както по-горе.
- Дали orphan подсборките се рендерират като подсборки, а не като детайли.

## Примерен фрагмент (getAssemblyChildren)
```js
function getAssemblyChildren(parentPath) {
    let _visitedPaths = arguments.length > 1 ? arguments[1] : new Set();
    if (_visitedPaths.has(parentPath)) {
        return children;
    }
    _visitedPaths = new Set(_visitedPaths);
    _visitedPaths.add(parentPath);
    // ...
    // рекурсивно извикване:
    const subChildren = getAssemblyChildren(child.path, new Set(_visitedPaths));
    // ...
}
```

## Заключение
Ако всички тези стъпки са изпълнени, ще има "+" пред всяко подасембли, независимо от нивото или класификацията му.
