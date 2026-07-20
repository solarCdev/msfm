import sys
from tokenizer import Tokenizer
from parser import Parser
from interpreter import Interpreter

def run_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"❌ [msfm Error] Files not found: {file_path}")
        return
    except Exception as e:
        print(f"❌ [msfm Error] Failed to read file: {e}")
        return

    # try:
    code += '\n'
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    
    parser = Parser(tokens)
    ast = parser.parse_program()
    
    interpreter = Interpreter()
    interpreter.interpret(ast)
        
    # except Exception as e:
    #     # 💡 에러 메시지에도 msfm 브랜딩을 적용합니다.
    #     print(f"\n❌ [msfm Runtime/Algebra Error]:\n{e}")

def main():
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        # 💡 실행 인자가 없을 때 msfm의 본래 의미와 사용법을 친절하게 안내합니다.
        print("==================================================")
        print(" msfm: Minimum Script for Math (MVP Engine)       ")
        print("==================================================")
        print("Usage: python main.py [path/to/script.msfm]")

if __name__ == "__main__":
    main()