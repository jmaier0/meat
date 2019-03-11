# MEtastability Analysis Tool (MEAT)

This tool implements various approaches to determine metastability in electronic circuits. A so called metastable state can be compared to a stick which is balanced on a palm: in the perfect position it will stand upright but only minor disturbance will cause it to approach its actual stable states.

Determining the metastable state is a very challenging task as the system tries to escape it as quickly as possible. Therefore this tools ipmlements some systematic and novel ways to circumvent that property. A detailled analysis of the methods has been published by Maier et al. at ASYNC'19.

Despite designed for characterizing Schmitt Triggers it turned out that the methods are applicable to other circuits as well. This has been already verified for the flip-flop however many more might still be undiscovered.

## Requirements

The tool was developed and tested with Python 2.6. Furthermore you need *SPICE* and a suitable technology library, which we use as golden reference for our analysis.

## File Structure

A big goal during development was to guarantee easy extendability. Therefore new circuits can be simply added by creating a new folder in 'circuits/' which needs to be filled with suitable *SPICE* files (\*.sp). The file names are hard coded and have to be set appropriately. Otherwise they will not be found.

Different technologies can be defined in 'technologies/'. Furthermore we used these files to define shared properties such as the load capacitance, which makes it possible to change it for all simulations in a single place.

To run a simulation one simply has to switch to 'bin/' (although it only contains scripts) and run **python charST.py --help**, which will display all available methods and options.
