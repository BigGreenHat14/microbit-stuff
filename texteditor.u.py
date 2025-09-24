def main(file):
    try:
        lines = read(file).replace("\r","").split("\n")
    except OSError:
        lines = []
    while True:
        print()
        for idx, line in enumerate(lines):
            print(str(idx+1) + ".",line)
        print()
        print("(R)eplace line")
        print("(N)ew line")
        print("(S)ave")
        print("(E)xit")
        option = input("? > ").lower()
        if option == "r":
            try:
                line = int(input("Line > ")) - 1
                lines[line] = input("Text > ")
            except:
                print("Enter a valid number")
        elif option == "n":
            lines.append("")
        elif option == "s":
            write(file,"\n".join(lines))
        elif option == "e":
            print()
            break