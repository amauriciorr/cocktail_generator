import pdf_parser

if __name__ == '__main__':
    bartender = open('source/1000bartender.pdf', 'rb') 
    boston = open('source/mr_boston.pdf', 'rb') 
    mr_boston_text = boston_parser(boston, 34, 285, True)
    bartender_text = bartender_parser(bartender, 28, 560)
