import sqlite3
import subprocess
from time import sleep
import os

def ExportBPMDataToAppleMusic(database_path):
    success_log_path = os.path.join('data', 'logs', 'BPM_success.log')
    error_log_path = os.path.join('data', 'logs', 'BPM_error.log')
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute('SELECT Title, persistent_id, bpm FROM Library WHERE bpm > 0 AND bpm IS NOT NULL')
    track_bpm_list = cursor.fetchall()

    conn.close()

    with open(success_log_path, 'a') as success_log, open(error_log_path, 'w') as error_log:
        for track_name, persistent_id, bpm in track_bpm_list:
            apple_script = f'''
            on editBPMByID(trackID, newBPM)
                try
                    tell application "Music"
                        set targetTrack to (first track of library playlist 1 whose persistent ID is trackID)
                        if targetTrack is not missing value then
                            set bpm of targetTrack to newBPM
                            return "BPM da faixa {persistent_id} atualizado com sucesso."
                        else
                            return "Faixa com ID " & trackID & " não encontrada."
                        end if
                    end tell
                on error errMsg number errNum
                    return "Erro: " & errMsg & " (Código do erro: " & errNum & ")"
                end try
            end editBPMByID

            -- Chamar a função com os parâmetros
            editBPMByID("{persistent_id}", {bpm})
            '''

            result = subprocess.run(['osascript', '-e', apple_script], capture_output=True, text=True)

            print(result.stdout)

            if "atualizado com sucesso" in result.stdout:
                success_log.write(f"{track_name} ({persistent_id}): BPM atualizado para {bpm}\n")
            else:
                error_log.write(f"{track_name} ({persistent_id}): Erro ao atualizar BPM. Mensagem: {result.stdout}\n")

            sleep(0.1)

def exportDataToAppleMusic(database_path):
    success_log_path = os.path.join('data', 'logs', 'Comments_success.log')
    error_log_path = os.path.join('data', 'logs', 'Comments_error.log')
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute('SELECT Title, persistent_id, Comments, Description FROM Library WHERE Comments IS NOT NULL OR Description IS NOT NULL')
    track_comments_list = cursor.fetchall()


    with open(success_log_path, 'a') as success_log, open(error_log_path, 'w') as error_log:
        for track_name, persistent_id, description, comments in track_comments_list:
            apple_script = f'''on editTrackByID(trackID, newDescription, newComment)
    try
        tell application "Music"
            -- Buscar a faixa com o ID fornecido
            set targetTrack to (first track of library playlist 1 whose persistent ID is trackID)
            -- Verificar se a faixa foi encontrada
            if targetTrack is not missing value then
                -- Alterar a descrição (usado como subgênero)
                set description of targetTrack to newDescription
                -- Alterar o comentário (usado como instrumentos)
                set comment of targetTrack to newComment
                return "Faixa " & trackID & " atualizada com sucesso."
            else
                return "Faixa com ID " & trackID & " não encontrada."
            end if
        end tell
    on error errMsg number errNum
        -- Tratamento de erros
        return "Erro: " & errMsg & " (Código do erro: " & errNum & ")"
    end try
end editTrackByID

-- Chamar a função com os parâmetros
editTrackByID("{persistent_id}", "{description}", "{comments}")'''

            result = subprocess.run(['osascript', '-e', apple_script], capture_output=True, text=True)

            print(result.stdout)

            if "atualizada com sucesso" in result.stdout:
                success_log.write(f"{track_name} ({persistent_id}): Descrição e comentários atualizados\n")
            else:
                error_log.write(f"{track_name} ({persistent_id}): Erro ao atualizar. Mensagem: {result.stdout}\n")

            sleep(0.1)




if __name__ == '__main__':
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    database_path = os.path.join(SCRIPT_DIR, 'data', 'main.db')

    exportDataToAppleMusic(database_path)
