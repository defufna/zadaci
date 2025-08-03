import random
import sys

#random.seed(32)  # For reproducibility
# Function to generate math problems
def generate_math_problems(n=20):
    problems = []
    answers = []
    operations = ['+', '-', '*', '/']
    while len(problems) < n:
        op = random.choice(operations)
        if op == '+':
            a, b = random.randint(1, 999), random.randint(1, 999)
            if a + b <= 1000:
                problems.append(f"{a} + {b}")
                answers.append(a + b)
        elif op == '-':
            a, b = random.randint(1, 999), random.randint(1, 999)
            if a - b >= 0:
                problems.append(f"{a} - {b}")
                answers.append(a - b)
        elif op == '*':
            for i in range(10):
                a, b = random.randint(2, 10), random.randint(2, 99)
                if random.randint(0,1) == 0:
                    a, b = b, a
                if a * b <= 1000:
                    problems.append(f"{a} \\cdot {b}")  # Use LaTeX \cdot for multiplication
                    answers.append(a * b)
                    break
        elif op == '/':
            for i in range(10):
                b = random.randint(2, 10)
                result = random.randint(2, 99)
                a = b * result
                if a <= 1000:
                    problems.append(f"{a} \\div {b}")  # Use LaTeX \div for division
                    answers.append(result)
                    break
    return problems[:n], answers[:n]

# Function to create LaTeX file
def create_math_latex(problems, title="Matematički Zadaci", footer = None):
    # LaTeX document header
    latex_content = r"""
\documentclass[a4paper,12pt]{article}
\usepackage[utf8]{inputenc}
\usepackage{amsmath}
\usepackage{parskip}
\usepackage{multicol}
\usepackage{geometry}
\usepackage{tabularx}
\usepackage{dashrule}
\usepackage{pifont}
\geometry{a4paper, margin=2cm}

\begin{document}

\begin{center}
    \textbf{\Large """ + title + r"""}
\end{center}

\vspace{1cm}

\begin{multicols}{2}
    \begin{enumerate}
"""

    # Add problems in LaTeX format
    for i, problem in enumerate(problems, 1):
        # Convert problem to LaTeX math mode
        latex_problem = problem.replace(" \\cdot ", " \\cdot ")  # Already formatted
        latex_problem = latex_problem.replace(" \\div ", " \\div ")  # Already formatted
        latex_content += f"        \\item ${latex_problem} =$\n"


    # LaTeX document footer
    latex_content += r"""
    \end{enumerate}
\end{multicols} """

    if footer:
        latex_content += footer

    latex_content += r"""
\end{document}
"""

    return latex_content


def print_help():
    print("Usage: python zadaci.py [number_of_problems] [filename]")
    print("       python zadaci.py cypher message [filename]")
    print("Generates a LaTeX document with math problems and compiles it to PDF.")
    print("If no arguments are provided, defaults to 20 problems and 'output.pdf' as filename.")

def parse_arguments():
    num_problems = 20  # Default number of problems
    cypher = False  # Default to not using cypher

    # Get number of problems and filename from command line arguments, print help if needed
    if len(sys.argv) > 1:
        if len(sys.argv) == 3 and sys.argv[1] == "cypher":
            cypher = True
            message = sys.argv[2]
        else:
            try:
                num_problems = int(sys.argv[1])
                if num_problems <= 0:
                    raise ValueError("Number of problems must be a positive integer.")
            except ValueError as e:
                print_help()
                return None

    filename = "output.pdf"

    if len(sys.argv) > 3:
        filename = sys.argv[2] if not cypher else sys.argv[3]

    return num_problems, cypher, message if cypher else None, filename


def create_cypher_content(message):
    alphabet = {letter:None for letter in set(message.replace(" ", ""))}
    num_problems = len(alphabet)
    problems, answers = generate_math_problems(num_problems)
  
    for letter in sorted(alphabet.keys(), reverse=True):
        alphabet[letter] = answers.pop()
    
    cypher_table = "\\begin{tabularx}{\\textwidth}{|" + "|".join([">{\\centering\\arraybackslash}X",]*len(alphabet)) + "|}\n"
    cypher_table += "\\hline\n"
    cypher_table += " & ".join(sorted(alphabet.keys())) + " \\\\\n"
    cypher_table += "\\hline\n"
    cypher_table += (" & " * (len(alphabet)-1)).strip() + " \\\\\n"
    cypher_table += "\\hline\n"
    cypher_table += "\\end{tabularx}\n"

    def create_letter_latex(number):
        return r"""
\begin{minipage}[t]{1cm}
    \vspace{1cm}
    \underline{\hspace{1cm}}
    \vspace{2mm}
    \centering """ + str(number) + r"""
\end{minipage}"""

    message_table = ""
    for letter in message:
        if letter == " ":
            message_table += "\n\\hspace{5mm}\n"
        else:
            number = alphabet.get(letter, 0)
            message_table += create_letter_latex(number)
  
    separator = r"""
\vspace{1cm}
\begin{center}
  \makebox[\textwidth]{%
    \llap{\raisebox{-0.3ex}{\ding{34}}\hspace{-10pt}}%
    \hdashrule[0.5ex]{\textwidth}{0.5pt}{4pt}%
    \rlap{\raisebox{-0.3ex}{\hspace{-20pt}\ding{34}}}%
  }
\end{center}
"""

    
    return create_math_latex(problems, title="Kriptovana poruka", footer=cypher_table + separator + message_table)

def main():
    args = parse_arguments()

    if args is None:
        return
    
    num_problems, cypher, message, filename = args
    
    content = ""

    if cypher:
        content = create_cypher_content(message)
    else:    
    # Generate problems and create LaTeX file
        problems, answers = generate_math_problems(num_problems)
        content = create_math_latex(problems)

    import subprocess
    process = subprocess.Popen( ["wsl", "bash", "-c", "podman run --replace -i --name latex_compile -w /data docker.io/blang/latex:ubuntu pdflatex"],
                                stdin=subprocess.PIPE)
    process.communicate(input=content.encode('utf-8'))
    process.stdin.close()
    process.wait()

    subprocess.run(["wsl", "podman", "cp", "latex_compile:/data/texput.pdf", filename])

if __name__ == "__main__":
    main()