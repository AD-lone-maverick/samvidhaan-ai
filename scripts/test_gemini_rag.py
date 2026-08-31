from gemini_client import generate_answer


question = "What does Article 368 say?"

context = """
Article 368 — Power of Parliament to amend the Constitution
and procedure therefor.

(1) Parliament may in exercise of its constituent power amend
the Constitution in accordance with the procedure laid down
in this article.

(2) An amendment may be initiated by introduction of a Bill
in either House of Parliament. The Bill must be passed in
each House by a majority of the total membership and by a
majority of not less than two-thirds of members present and
voting.
"""


answer = generate_answer(
    question,
    context
)


print("\n" + "=" * 70)
print("GEMINI ANSWER")
print("=" * 70)
print(answer)