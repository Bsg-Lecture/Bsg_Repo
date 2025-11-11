import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;

public class BomBom {

    private static final int ROWS = 10;
    private static final int COLUMNS = 10;

    private static char[][] map;

    public static void main(String[] args) throws FileNotFoundException {
        // Haritayı dosyadan okuyun
        readMap("map.txt");

        // Oyunu başlatın
        play();
    }

    private static void readMap(String fileName) throws FileNotFoundException {
        // Dosyayı açın
        File file = new File(fileName);
        Scanner scanner = new Scanner(file);

        // Haritayı dizilere aktarın
        map = new char[ROWS][COLUMNS];
        for (int row = 0; row < ROWS; row++) {
            for (int column = 0; column < COLUMNS; column++) {
                map[row][column] = scanner.next().charAt(0);
            }
        }
    }

    private static void play() {
        // Oyun devam ediyor mu?
        boolean playing = true;

        // Kullanıcıdan koordinat girmesini isteyin
        while (playing) {
            System.out.println("Lütfen koordinat giriniz: ");
            Scanner scanner = new Scanner(System.in);
            int row = scanner.nextInt();
            int column = scanner.nextInt();

            // Koordinatı kontrol edin
            if (row < 0 || row >= ROWS || column < 0 || column >= COLUMNS) {
                System.out.println("Geçersiz koordinat!");
                continue;
            }

            // Koordinatı değiştirin
            char number = map[row][column];
            removeNumber(row, column, number);

            // Oyun bitti mi?
            if (isGameOver()) {
                System.out.println("Oyun bitti!");
                playing = false;
            }

            // Haritayı ekrana yazdırın
            printMap();
        }
    }

    private static void removeNumber(int row, int column, char number) {
        // Koordinatı değiştirin
        map[row][column] = 'X';

        // Komşu hücreleri kontrol edin
        for (int i = -1; i <= 1; i++) {
            for (int j = -1; j <= 1; j++) {
                if (i == 0 && j == 0) {
                    continue;
                }

                int nextRow = row + i;
                int nextColumn = column + j;

                if (isInsideMap(nextRow, nextColumn) && map[nextRow][nextColumn] == number) {
                    removeNumber(nextRow, nextColumn, number);
                }
            }
        }
    }

    private static boolean isInsideMap(int row, int column) {
        return row >= 0 && row < ROWS && column >= 0 && column < COLUMNS;
    }

    private static boolean isGameOver() {
        for (int row = 0; row < ROWS; row++) {
            for (int column = 0; column < COLUMNS; column++) {
                if (map[row][column] != 'X') {
                    return false;
                }
            }
        }

        return true;
    }

    private static void printMap() {
        for (int row = 0; row < ROWS; row++) {
            for (int column = 0; column < COLUMNS; column++) {
                System.out.print(map[row][column]);
            }
            System.out.println();
        }
    }
}