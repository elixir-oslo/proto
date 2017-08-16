/**
 * @author Kjetil
 */
public class MarkovModel {

 public static char[] DNABases={'A','C','G','T'};

    /** Converts an index from a frequency table into the corresponding DNA oligo
     *  @param index
     *  @param length The size of the oligo to be returned
     */
    public static char[] indexToOligo(int index, int length) {
        char[] oligo=new char[length];
        if (length==0) return oligo;
        for (int i=length-1;i>=0;i--) {
            oligo[i]=DNABases[index%4];
            index=index/4;
        }
        return oligo;
    }

    /** Converts a DNA oligo into a number which can serve as an index into frequency tables */
    public static int oligoToIndex(char[] oligo) {
        int size=oligo.length;
        int result=0;
        for (int i=0;i<size;i++) {
            char c=oligo[size-i-1];
            int index=0;
            switch (c) {
               case 'A': case 'a': index=0; break;
               case 'C': case 'c': index=1; break;
               case 'G': case 'g': index=2; break;
               case 'T': case 't': index=3; break;
               default: return -1; // not a valid oligo. Contains non-base characters
            }
            result+=index*(int)Math.pow(4, i);
        }
        return result;
    }

    /**
     * Determines the frequency of each oligo of a given size in a sequence
     * @param oligosize Wordsize of oligos to be counted
     * @return A double[] array with normalized frequencies for each oligo of the specified length
     */
    public static double[] countOligoFrequencies(char[] sequence, int oligosize) {
        double[] frequencies=new double[(int)Math.pow(4, oligosize)];
        int size=0;
        for (int i=0;i<=sequence.length-oligosize;i++) {
            char[] oligo=java.util.Arrays.copyOfRange(sequence, i, i+oligosize); // note that the "end-position" (i+oligosize) is exclusive in the range!
            int index=oligoToIndex(oligo);
            if (index>=0) { // Only consider oligos with valid bases (A,C,G,T). Skip other oligos (e.g. those containing N's)
                frequencies[index]+=1;
                size++;
            }
        }
        for (int i=0;i<frequencies.length;i++) {
            frequencies[i]=frequencies[i]/(double)size; // normalize counts to frequencies
        }
        return frequencies;
    }

    public static double[] convertFrequencyTableToTransitionMatrix(double[] table) {
         // Each block of 4 consecutive entries (prefix+A,prefix+C,prefix+G,prefix+T) should sum to 1
        for (int i=0;i<table.length;i+=4) {
            double total=table[i]+table[i+1]+table[i+2]+table[i+3];
            table[i]  =table[i]/total;
            table[i+1]=table[i+1]/total;
            table[i+2]=table[i+2]/total;
            table[i+3]=table[i+3]/total;
        }
        return table;
    }

     /**
     * Returns a randomly selected oligo of length equal to the model order
     * This oligo can be used as a prefix to start off sequence generation.
     * The oligo is chosen according to the probabilities in the frequency table
     * @return
     */
    public static char[] selectPrefix(int modelorder, double[] frequencies) {
        if (modelorder==0) return new char[0];
        double sum=0;
        double random=Math.random();
        for (int i=0;i<frequencies.length;i++) {
            sum+=frequencies[i];
            if (random<sum) return indexToOligo(i, modelorder);
        }
        return indexToOligo(frequencies.length-1, modelorder); // This should normally happen, but I have it here in case of rounding errors
    }

    /**
     * Given an oligo as prefix, this method returns a suitable next base according to the provided transition matrix
     * @param prefix This should have length equal to model order!
     * @return
     */
    public static char getNextBase(char[] prefix, double[] transitionmatrix) {
        char[] prefixPlusA=new char[prefix.length+1]; // An array to hold the prefix plus one more letter (A)
        System.arraycopy(prefix, 0, prefixPlusA, 0, prefix.length); // Insert the prefix at the start of the extended prefix
        prefixPlusA[prefixPlusA.length-1]='A'; // Add an A to the prefix to get the word "prefix+A"
        int index=oligoToIndex(prefixPlusA); // This index will now point to the location of the word "prefix+A" in the transition matrix
        double probA=transitionmatrix[index];   // Obtain the probabilities for each of the 4 possible transitions
        double probC=transitionmatrix[index+1]; // these will be in order A,C,G,T
        double probG=transitionmatrix[index+2]; // Actually, the probability of transition to T is not needed since the four must sum to 1 anyway
        double selected=Math.random();
             if (selected<probA) return 'A';
        else if (selected<probA+probC) return 'C';
        else if (selected<probA+probC+probG) return 'G';
        else return 'T';
    }

    /** Generates a new DNA sequence of the given length based on the markov model */
    public static char[] generateSequence(int length, int modelorder, double[] oligofrequencies, double[] transitionmatrix) {
        char[] buffer=new char[length]; // the length should be larger than the order...
        char[] prefix=selectPrefix(modelorder, oligofrequencies);
        System.arraycopy(prefix, 0, buffer, 0, prefix.length); // Insert the prefix at the start of the buffer
        for (int i=prefix.length;i<length;i++) { // now fill in the rest of the buffer in a loop
            System.arraycopy(buffer, i-prefix.length, prefix, 0, prefix.length); // select new prefix based on the last N characters added to the buffer
            buffer[i]=getNextBase(prefix,transitionmatrix); // select next base and insert it at the end of the buffer
        }
        return buffer;
    }

    /** Reads the first line from a file and returns it as a String
     *  (If the first line is a FASTA-header the second line will be returned)
     */
    public static String readSingleDNAStringFromFile(String filename) {
      java.io.FileInputStream fstream=null;
      java.io.BufferedReader br=null;
      String line="";
      try {
          fstream = new java.io.FileInputStream(filename);
          br = new java.io.BufferedReader(new java.io.InputStreamReader(fstream));
          line = br.readLine();
          if (line.startsWith(">")) line=br.readLine(); // Skip FASTA header. Read next line
          br.close();
       } catch (Exception e){e.printStackTrace(System.err);}
      return line;
    }

    /**
     * This method constructs a Markov Model of a specified order from a DNA sequence and then
     * uses this model to generate a new DNA sequence with a given length
     * @param args All arguments are optional
     *  If provided, they are in order
     *   - A filename for the source sequence (Must contain a DNA sequence on the first line (single line) or on the second line if the first line is a FASTA header)
     *   - The Markov Model order (default 3)
     *   - The length of the sequence to generate (default 1000)
     *
     * Example usage:   java MarkovModel <fastafile> <markovorder> <sequencelength>
     */
    public static void main(String[] args) {
        String dna="ATCGATGATAGGCGATAGATCGATCGAGTCAGGATGGAGAGAGCTCGAGAGATCGAGAATAGCTAGAGTAGATATA"; // just an example which can be substituted later with a sequence read from file
        int markovOrder=3;
        int newsequencelength=1000;
        if (args.length>0) dna=readSingleDNAStringFromFile(args[0]);
        if (args.length>1) try {markovOrder=Integer.parseInt(args[1]);} catch (NumberFormatException e) {System.err.println("Markov order error");}
        if (args.length>2) try {newsequencelength=Integer.parseInt(args[2]);} catch (NumberFormatException e) {System.err.println("Sequence length error");}
        char[] sourceSequence=dna.toCharArray(); // The sourceSequence is the sequence we will base the Markov Model on
        double[] oligoFrequencies=countOligoFrequencies(sourceSequence,markovOrder);
        double[] transitionMatrix=countOligoFrequencies(sourceSequence,markovOrder+1);
        // debug(oligoFrequencies,markovOrder);
        // debug(transitionMatrix,markovOrder+1);
        transitionMatrix=convertFrequencyTableToTransitionMatrix(transitionMatrix);
        char[] newsequence=generateSequence(newsequencelength, markovOrder, oligoFrequencies, transitionMatrix);
        System.out.println(new String(newsequence));
    }

    /** Print out a frequency table for debugging purposes */
    private static void debug(double[] frequencytable, int order) {
        for (int i=0;i<frequencytable.length;i++) {
            System.out.print(indexToOligo(i, order));
            System.out.print(" => ");
            System.out.println(frequencytable[i]);
        }
    }

}
